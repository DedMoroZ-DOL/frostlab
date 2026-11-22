# Frost Lab Report 002 - code snapshot

2편 "픽셀 수만 늘리면?" (SD1.5, 정사각형 512 → 768 → 1024 → 1536) 측정에 쓴 코드와 워크플로.

| 파일 | 내용 | sha256 |
| --- | --- | --- |
| frostlab_bench.py | 측정 스크립트 v1.2 (Claude 작성) | `a81864fc92425810cd623b7486428074ba37d440b86ec3b88998dbf2491a180e` |
| sd15_api.json | ComfyUI 기본 워크플로 (Export API, 512×512) | `60ab6ad6318dd34ee70eaf6cd64f40f1ecfd5327c1f99718adfd8417f2f9f255` |
| run_report002.bat | Report 002·003 측정 실행 파일 | `2b7747c00287f1068f219dd082ede8cf96dcc1e122f62ea4eb1fc727f4687751` |

## 측정 방식

- 측정 스크립트 v1.2, `--mode speed`만 쓴다 (표준 프롬프트 3개 × 시드 5개 = 15장, 첫 실행 1장은 따로 기록).
- 배치 측정과 한계 측정은 하지 않는다.
- 해상도는 워크플로가 아니라 `--width`/`--height` 인자로 바꾼다. 워크플로 파일은 Report 001과 같은 512×512 그대로이므로, 512가 아닌 측정에서는 해상도가 다르다는 안내가 출력되는 것이 정상이다.
- Report 002와 003은 같은 날 한 번에 측정했고, 512×512 기준값을 함께 쓴다. 기준값은 Report 002 폴더의 `5070ti_512x512`에 있다.
- 마지막에 512×512를 한 번 더 재서(`5070ti_512x512_end`) 하루 동안 측정값이 흔들렸는지 확인한다.

## 실행 환경

Report 001과 같은 환경(Comfy Desktop, ComfyUI 0.45.5, PyTorch 2.12.1+cu130, NVIDIA 드라이버 621.24, RTX 5070 Ti)에서 재는 것이 원칙이다.
실제로 잰 환경은 각 결과 폴더의 env.json에 있다.
실행: frostlab 폴더에서 `run_report002.bat` 실행.
