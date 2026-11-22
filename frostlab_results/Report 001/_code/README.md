# Frost Lab Report 001 - code snapshot

창간호 "그래픽카드를 바꾸면, 뭐가 달라질까?" (RTX 3070 -> RTX 5070 Ti) 측정에 쓴 코드와 워크플로.

| 파일 | 내용 | sha256 |
| --- | --- | --- |
| frostlab_bench.py | 측정 스크립트 (Claude 작성) | 4a4c02f9a05f08ef... |
| sd15_api.json | ComfyUI 기본 워크플로 (Export API) | 60ab6ad6318dd34e... |
| run_5070ti.bat | 5070 Ti 측정 실행 파일 | b031b6f612a345e2... |

## 스크립트 개정 기록

- 3070 측정(2026-11-17, 3070_basic / 3070_limit)은 이 스냅숏보다 앞선 판으로 실행했다.
  차이는 기록 항목뿐이고 측정 방식은 같다.
  - 추가: vram_used_idle_mb (모델을 내린 뒤 VRAM 사용량)
  - 추가: script_sha256, workflow_sha256 (env.json에 코드 지문 기록)
- 5070 Ti 측정부터는 이 판을 쓴다. env.json의 script_sha256으로 확인할 수 있다.

## 실행 환경

Comfy Desktop (ComfyUI 0.45.5), PyTorch 2.12.1+cu130, NVIDIA 드라이버 621.24.
실행: frostlab 폴더에서 ComfyUI의 .venv 파이썬으로 frostlab_bench.py 실행 (run_5070ti.bat 참고).
