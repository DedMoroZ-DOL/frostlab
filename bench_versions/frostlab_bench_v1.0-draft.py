r"""
Frost Lab 창간호 측정 스크립트 — 그래픽카드를 바꾸면, 뭐가 달라질까?

ComfyUI API로 같은 워크플로를 같은 조건에서 반복 실행하고,
장당 시간 · 샘플링 it/s · VRAM/전력/온도 최대치를 CSV로 남긴다.
추가 설치 필요 없음 (ComfyUI에 들어 있는 aiohttp만 사용).

준비
  1) ComfyUI를 새로 켠다 (게임, 브라우저 영상 등 GPU 쓰는 건 꺼 둔다)
  2) KSampler가 1개인 기본 SD1.5 워크플로를 열고
     Workflow 메뉴 → Export (API) 로 이 폴더에 sd15_api.json 저장
     (일반 Save 파일은 안 됨)

실행 (Comfy Desktop 기준, 이 폴더에서 명령창 열고)
  ..\ComfyUI-Installs\ComfyUI\ComfyUI\.venv\Scripts\python.exe frostlab_bench.py --gpu-label 3070 --workflow sd15_api.json
  5070 Ti 장착 후:  --gpu-label 5070ti --batches 1,2,4,8,16

결과
  frostlab_results/<라벨>_speed.csv   속도 측정 (프롬프트 3개 × 시드 5개)
  frostlab_results/<라벨>_batch.csv   배치 한계 측정
  frostlab_results/<라벨>_env.json    GPU·드라이버·PyTorch·ComfyUI 버전, 첫 실행 시간
  이미지는 ComfyUI output/frostlab/<라벨>/ 에 저장 (GPU 간 같은 시드 비교용)
"""

import argparse
import asyncio
import copy
import csv
import json
import os
import statistics
import subprocess
import sys
import threading
import time
import uuid
from datetime import datetime

try:
    import aiohttp
except ImportError:
    sys.exit("aiohttp가 없습니다. ComfyUI의 .venv 파이썬으로 실행해 주세요.")

# ── 고정 조건 ──────────────────────────────────────────────
# 사람이 나오지 않는, 성격이 다른 세 장면. 바꾸고 싶으면 여기만 고치면 됨.
PROMPTS = [
    "misty mountain lake at dawn, pine forest, soft light, highly detailed landscape",
    "still life of ceramic teapot and lemons on a wooden table, window light, oil painting",
    "empty library interior with tall bookshelves and a spiral staircase, warm lamps",
]
# '5회 반복' 대신 고정된 시드 5개. 같은 입력을 다시 넣으면 ComfyUI가 캐시 결과를
# 돌려줘서 실제 생성이 안 일어나기 때문. 두 GPU가 같은 목록을 쓰므로
# (프롬프트, 시드) 쌍끼리 그림 비교가 가능하다.
SEEDS = [1001, 1002, 1003, 1004, 1005]
WARMUP_SEED = 999
WIDTH = HEIGHT = 512
# ─────────────────────────────────────────────────────────


def smi(fields, gpu_index):
    out = subprocess.run(
        ["nvidia-smi", f"-i={gpu_index}", f"--query-gpu={fields}",
         "--format=csv,noheader,nounits"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    return [x.strip() for x in out.split(",")]


def to_float(x):
    try:
        return float(x)
    except ValueError:
        return None


class GpuMonitor(threading.Thread):
    """생성 중 0.1초마다 nvidia-smi를 읽어 최대치를 기록."""

    def __init__(self, gpu_index):
        super().__init__(daemon=True)
        self.gpu_index = gpu_index
        self.stop_evt = threading.Event()
        self.peak = {"vram": None, "power": None, "temp": None}

    def run(self):
        while not self.stop_evt.is_set():
            try:
                vals = smi("memory.used,power.draw,temperature.gpu", self.gpu_index)
                for key, v in zip(("vram", "power", "temp"), vals):
                    v = to_float(v)
                    if v is not None and (self.peak[key] is None or v > self.peak[key]):
                        self.peak[key] = v
            except Exception:
                pass
            time.sleep(0.1)

    def stop(self):
        self.stop_evt.set()
        self.join(timeout=3)


def find_nodes(wf):
    if "nodes" in wf:
        sys.exit("일반 저장 형식입니다. Workflow → Export (API) 로 다시 저장해 주세요.")
    ks_ids = [k for k, v in wf.items() if v.get("class_type") == "KSampler"]
    if not ks_ids:
        sys.exit("워크플로에서 KSampler 노드를 찾지 못했습니다.")
    if len(ks_ids) > 1:
        sys.exit("KSampler가 2개 이상입니다(하이레즈 픽스 등). "
                 "측정에는 KSampler 1개짜리 기본 워크플로를 써 주세요.")
    ks_id = ks_ids[0]
    ks = wf[ks_id]["inputs"]
    pos_id = ks["positive"][0]
    lat_id = ks["latent_image"][0]
    if wf[lat_id]["class_type"] != "EmptyLatentImage":
        sys.exit("KSampler의 latent 입력이 EmptyLatentImage가 아닙니다.")
    save_ids = [k for k, v in wf.items() if v.get("class_type") == "SaveImage"]
    if not save_ids:
        sys.exit("SaveImage 노드를 찾지 못했습니다.")
    return ks_id, pos_id, lat_id, save_ids[0]


def build(wf, ids, prompt, seed, batch, prefix):
    ks_id, pos_id, lat_id, save_id = ids
    w = copy.deepcopy(wf)
    w[pos_id]["inputs"]["text"] = prompt
    w[ks_id]["inputs"]["seed"] = seed
    w[lat_id]["inputs"].update(width=WIDTH, height=HEIGHT, batch_size=batch)
    w[save_id]["inputs"]["filename_prefix"] = prefix
    return w


async def run_one(session, ws, base, client_id, workflow, ks_id, gpu_index):
    mon = GpuMonitor(gpu_index)
    mon.start()
    t0 = time.perf_counter()
    async with session.post(f"{base}/prompt",
                            json={"prompt": workflow, "client_id": client_id}) as r:
        body = await r.json()
    if "prompt_id" not in body:
        mon.stop()
        return dict(total_sec="", sampling_its="", peak_vram_mb="", peak_power_w="",
                    peak_temp_c="", status="rejected",
                    error=json.dumps(body, ensure_ascii=False)[:300])
    pid = body["prompt_id"]

    t_first = t_last = steps_max = None
    status, err = "ok", ""
    while True:
        msg = await ws.receive(timeout=900)
        if msg.type == aiohttp.WSMsgType.BINARY:  # 미리보기 이미지
            continue
        if msg.type != aiohttp.WSMsgType.TEXT:
            status, err = "error", f"websocket closed ({msg.type})"
            break
        m = json.loads(msg.data)
        typ, data = m.get("type"), m.get("data") or {}
        if data.get("prompt_id") not in (None, pid):
            continue
        if typ == "progress" and data.get("node") in (None, ks_id):
            now = time.perf_counter()
            if data.get("value") == 1:
                t_first = now
            if data.get("value") == data.get("max"):
                t_last, steps_max = now, data.get("max")
        elif typ == "execution_error":
            status = "error"
            err = (data.get("exception_message") or "").strip().splitlines()[0][:200]
        elif typ == "executing" and data.get("node") is None and data.get("prompt_id") == pid:
            break
    total = time.perf_counter() - t0
    mon.stop()

    its = None
    if t_first and t_last and steps_max and steps_max > 1 and t_last > t_first:
        its = (steps_max - 1) / (t_last - t_first)
    if status == "error" and "out of memory" in err.lower():
        status = "oom"
    return dict(total_sec=round(total, 3), sampling_its=round(its, 3) if its else "",
                peak_vram_mb=mon.peak["vram"], peak_power_w=mon.peak["power"],
                peak_temp_c=mon.peak["temp"], status=status, error=err)


FIELDS = ["gpu", "mode", "prompt_idx", "seed", "batch", "total_sec", "sec_per_image",
          "sampling_its", "peak_vram_mb", "peak_power_w", "peak_temp_c",
          "status", "error", "timestamp"]


def now_iso():
    return datetime.now().isoformat(timespec="seconds")


async def main_async(a):
    with open(a.workflow, encoding="utf-8") as f:
        wf = json.load(f)
    ids = find_nodes(wf)
    ks_in = wf[ids[0]]["inputs"]
    os.makedirs(a.out, exist_ok=True)
    label = a.gpu_label
    base = f"http://{a.server}"
    env_path = os.path.join(a.out, f"{label}_env.json")

    async with aiohttp.ClientSession() as session:
        async with session.get(f"{base}/system_stats") as r:
            stats = await r.json()
        name, driver, vram_total, vram_before = smi(
            "name,driver_version,memory.total,memory.used", a.gpu_index)
        sysinfo = stats.get("system", {})
        env = {
            "label": label, "measured_at": now_iso(),
            "gpu": name, "driver": driver, "vram_total_mb": vram_total,
            "vram_used_before_mb": vram_before,
            "comfyui_version": sysinfo.get("comfyui_version"),
            "pytorch_version": sysinfo.get("pytorch_version"),
            "python_version": sysinfo.get("python_version"),
            "checkpoint": next((v["inputs"].get("ckpt_name") for v in wf.values()
                                if v.get("class_type") == "CheckpointLoaderSimple"), None),
            "steps": ks_in.get("steps"), "cfg": ks_in.get("cfg"),
            "sampler": ks_in.get("sampler_name"), "scheduler": ks_in.get("scheduler"),
            "resolution": f"{WIDTH}x{HEIGHT}", "prompts": PROMPTS, "seeds": SEEDS,
        }
        print(json.dumps(env, ensure_ascii=False, indent=2))

        client_id = str(uuid.uuid4())
        async with session.ws_connect(f"ws://{a.server}/ws?clientId={client_id}",
                                      max_msg_size=0) as ws:
            # 모델을 내리고 '첫 실행(모델 로딩 포함)' 시간을 잰다. 평균에서는 뺀다.
            async with session.post(f"{base}/free",
                                    json={"unload_models": True, "free_memory": True}):
                pass
            await asyncio.sleep(2)
            warm = await run_one(session, ws, base, client_id,
                                 build(wf, ids, PROMPTS[0], WARMUP_SEED, 1,
                                       f"frostlab/{label}/warmup"),
                                 ids[0], a.gpu_index)
            env["first_run_sec"] = warm["total_sec"]
            env["first_run_status"] = warm["status"]
            with open(env_path, "w", encoding="utf-8") as f:
                json.dump(env, f, ensure_ascii=False, indent=2)
            print(f"[첫 실행·모델 로딩 포함] {warm['total_sec']}초 [{warm['status']}] {warm['error']}")
            if warm["status"] != "ok":
                sys.exit("첫 실행부터 실패했습니다. 위 오류 메시지를 확인해 주세요.")

            if a.mode in ("speed", "all"):
                rows = []
                with open(os.path.join(a.out, f"{label}_speed.csv"), "w",
                          newline="", encoding="utf-8-sig") as f:
                    w = csv.DictWriter(f, fieldnames=FIELDS)
                    w.writeheader()
                    for pi, p in enumerate(PROMPTS):
                        for s in SEEDS:
                            r = await run_one(session, ws, base, client_id,
                                              build(wf, ids, p, s, 1,
                                                    f"frostlab/{label}/p{pi}_s{s}"),
                                              ids[0], a.gpu_index)
                            row = dict(gpu=label, mode="speed", prompt_idx=pi, seed=s,
                                       batch=1, sec_per_image=r["total_sec"],
                                       timestamp=now_iso(), **r)
                            w.writerow(row)
                            f.flush()
                            rows.append(row)
                            print(f"  p{pi} s{s}: {r['total_sec']}초, {r['sampling_its']} it/s, "
                                  f"VRAM {r['peak_vram_mb']}MB [{r['status']}] {r['error']}")
                ok = [r for r in rows if r["status"] == "ok"]
                if ok:
                    t = [r["total_sec"] for r in ok]
                    its = [r["sampling_its"] for r in ok if r["sampling_its"] != ""]
                    line = (f"\n[속도 요약] 성공 {len(ok)}/{len(rows)}장, 장당 평균 "
                            f"{statistics.mean(t):.3f}초 (표준편차 {statistics.pstdev(t):.3f})")
                    if its:
                        line += f", 평균 {statistics.mean(its):.2f} it/s"
                    print(line)

            if a.mode in ("batch", "all"):
                with open(os.path.join(a.out, f"{label}_batch.csv"), "w",
                          newline="", encoding="utf-8-sig") as f:
                    w = csv.DictWriter(f, fieldnames=FIELDS)
                    w.writeheader()
                    for b in [int(x) for x in a.batches.split(",")]:
                        r = await run_one(session, ws, base, client_id,
                                          build(wf, ids, PROMPTS[0], SEEDS[0], b,
                                                f"frostlab/{label}/batch{b}"),
                                          ids[0], a.gpu_index)
                        spi = round(r["total_sec"] / b, 3) if r["total_sec"] != "" else ""
                        row = dict(gpu=label, mode="batch", prompt_idx=0, seed=SEEDS[0],
                                   batch=b, sec_per_image=spi, timestamp=now_iso(), **r)
                        w.writerow(row)
                        f.flush()
                        print(f"  batch {b}: {r['total_sec']}초 (장당 {spi}초), "
                              f"VRAM {r['peak_vram_mb']}MB [{r['status']}] {r['error']}")
                        if r["status"] != "ok":
                            print("  → 실패 지점 도달, 배치 측정 중단")
                            break

    print(f"\n완료. 결과: {os.path.abspath(a.out)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gpu-label", required=True, help="예: 3070, 5070ti")
    ap.add_argument("--workflow", required=True, help="Export (API)로 저장한 json")
    ap.add_argument("--server", default="127.0.0.1:8188")
    ap.add_argument("--gpu-index", default="0")
    ap.add_argument("--mode", choices=["speed", "batch", "all"], default="all")
    ap.add_argument("--batches", default="1,2,4,8")
    ap.add_argument("--out", default="frostlab_results")
    a = ap.parse_args()
    asyncio.run(main_async(a))


if __name__ == "__main__":
    main()
