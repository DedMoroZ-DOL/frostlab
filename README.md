# Frost Lab · 주간 실증 프로젝트

> 이걸 바꾸면, 뭐가 달라질까?

내 PC에서 생성형 이미지 AI(ComfyUI)를 직접 돌리고, 변수를 하나씩만 바꿔 가며 결과를 데이터로 기록하는 실증 블로그의 측정 코드와 결과 저장소입니다.

- 블로그: [Frost Lab (네이버 블로그)](https://blog.naver.com/seraph7488)
- 작성자: DedMoroZ

AI와 함께 설계하고 분석하며, 실험과 판단은 사람이 합니다. 측정 스크립트는 Claude가 작성했습니다.

## 연재

| 편 | 주제 | 결과 폴더 | 측정부 |
| --- | --- | --- | --- |
| Report 001 | [그래픽카드를 바꾸면 (RTX 3070 → RTX 5070 Ti)](https://blog.naver.com/seraph7488/224487051256) | `frostlab_results/Report 001` | v1.0 (3070), v1.1 (5070 Ti) |
| Report 002 | 픽셀 수만 늘리면 (준비 중) | | v1.2 |
| Report 003 | 비율만 바꾸면 (준비 중) | | v1.2 |

## 폴더 구조

| 경로 | 내용 |
| --- | --- |
| `frostlab_bench.py` | 측정 스크립트 작업본 (계속 바뀜) |
| `sd15_api.json` | SD1.5 기본 워크플로 (ComfyUI Export API) |
| `CHANGELOG.md` | 측정 스크립트 버전과 개정 기록 |
| `bench_versions/` | 측정 스크립트 버전별 보존 사본과 sha256 |
| `run_versions/` | 편별 실행 파일 보존 사본과 실행 방법 |
| `frostlab_results/Report NNN/` | 편별 측정 결과(CSV, env.json), 그림, 그 편에 쓴 코드 사본(`_code`) |

작업본과 보존 사본을 나눠 둡니다. 보존 사본과 지난 편의 `_code`는 고치지 않습니다.

## 측정 방법

ComfyUI API로 같은 워크플로를 같은 조건에서 반복 실행하고, 장당 시간 · 샘플링 it/s · VRAM/전력/온도 최대치를 기록합니다.

- 표준 프롬프트 세트 v1: 풍경·정물·실내 프롬프트 3개 × 시드 1001–1005
- 대표값은 중앙값. 두 조건의 차이가 3% 미만이면 "차이 없음", 3–5%는 "경계", 5% 이상이면 "달라짐"
- 결과마다 `env.json`에 GPU·드라이버·ComfyUI·PyTorch 버전과 스크립트·워크플로의 sha256이 남습니다 (v1.1부터)

## 재현하기

1. ComfyUI를 켜고, KSampler가 1개인 기본 워크플로를 Workflow → Export (API)로 저장합니다.
2. ComfyUI에 들어 있는 파이썬(aiohttp 포함)으로 실행합니다. 추가 설치는 필요 없습니다.

```
python frostlab_bench.py --gpu-label 5070ti --workflow sd15_api.json --out "frostlab_results/Report 001/5070ti_basic"
```

| 인자 | 기본값 | 설명 |
| --- | --- | --- |
| `--gpu-label` | (필수) | 결과 파일 이름에 붙는 라벨 |
| `--workflow` | (필수) | Export (API)로 저장한 워크플로 |
| `--mode` | `all` | `speed`(15장 속도 측정), `batch`(배치 한계), `all` |
| `--batches` | `1,2,4,8` | 배치 측정 크기 목록 |
| `--width`, `--height` | `512` | 측정 해상도 (v1.2부터) |
| `--out` | `frostlab_results` | 결과 저장 폴더 |

편마다 실제로 쓴 명령은 `run_versions/README.md`에 있습니다.

## 라이선스

코드는 [MIT License](LICENSE)를 따릅니다.
