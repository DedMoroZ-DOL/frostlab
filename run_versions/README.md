# 실행 파일 보관

편마다 측정을 실행한 방법을 남긴다. 사본은 고치지 않는다. 다음 편부터는 `reportNNN_run_*.bat` 사본을 추가하고 이 표에 한 줄을 더한다.

| 편 | 측정 | 실행 방법 | sha256 | 측정부 |
| --- | --- | --- | --- | --- |
| Report 001 | 3070 (3070_basic, 3070_limit) | 배치 파일 없음. CMD에 명령을 직접 입력 (아래 명령) | 없음 | v1.0 |
| Report 001 | 5070 Ti (5070ti_basic, 5070ti_limit) | `report001_run_5070ti.bat` | `b031b6f612a345e2569070e93c969b11fcb5e29d937efd5eb606785b889cdaf7` | v1.1 |

배치 파일은 5070 Ti 측정부터 썼다.

## 3070 측정 명령 (확인됨)

3070 측정은 `frostlab` 폴더에서 CMD에 직접 입력했다. 아래 명령은 당시 Claude 대화 기록(명령창 출력 화면)에서 옮긴 것이며, 각 결과 env.json의 `label`·`measured_at`과 일치하는 것을 확인했다(2026-11-21).

```
..\ComfyUI-Installs\ComfyUI\ComfyUI\.venv\Scripts\python.exe frostlab_bench.py --gpu-label 3070 --workflow sd15_api.json
```

- 결과: 3070_basic (속도 15장 + 배치 1·2·4·8장). env.json: label `3070`, measured_at `2026-11-17T19:19:28`
- `--mode`를 생략해 기본값 `all`로 실행됐다.
- `--out`을 생략해 기본 폴더 `frostlab_results`에 저장됐고, 이후 `Report 001\3070_basic`으로 옮겼다.

```
..\ComfyUI-Installs\ComfyUI\ComfyUI\.venv\Scripts\python.exe frostlab_bench.py --gpu-label 3070x --mode batch --batches 16,32,64 --workflow sd15_api.json --out "frostlab_results\Report 001\3070_limit"
```

- 결과: 3070_limit. env.json: label `3070x`, measured_at `2026-11-17T19:26:22`

5070 Ti용 배치 파일은 이 두 명령의 순서와 인자를 그대로 따라 만들었다(결과 폴더는 처음부터 `--out`으로 지정).
