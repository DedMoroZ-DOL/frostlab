# Frost Lab · The Weekly Experiment

[한국어](README.md) | **English**

> What changes if I change this?

Measurement code and results for an experiment blog: I run generative image AI (ComfyUI) on my own PC, change one variable at a time, and record the results as data. The write-ups are in Korean; the code and data here are language-neutral.

- Blog: [Frost Lab (Naver Blog, Korean)](https://blog.naver.com/seraph7488)
- Author: DedMoroZ

Experiments are designed and analyzed together with AI; running the experiments and making the calls is done by a person. The measurement script was written by Claude.

## Series

| Report | Topic | Results folder | Script version |
| --- | --- | --- | --- |
| Report 001 | [Changing the GPU (RTX 3070 → RTX 5070 Ti)](https://blog.naver.com/seraph7488/224487051256) | `frostlab_results/Report 001` | v1.0 (3070), v1.1 (5070 Ti) |
| Report 002 | Raising only the pixel count (in preparation) | | v1.2 |
| Report 003 | Changing only the aspect ratio (in preparation) | | v1.2 |

## Folder structure

| Path | Contents |
| --- | --- |
| `frostlab_bench.py` | Working copy of the measurement script (keeps changing) |
| `sd15_api.json` | Default SD1.5 workflow (ComfyUI Export API) |
| `CHANGELOG.md` | Script versions and revision history (Korean) |
| `bench_versions/` | Preserved copy of each script version, with sha256 |
| `run_versions/` | Preserved copies of each report's run files and how they were run |
| `frostlab_results/Report NNN/` | Each report's results (CSV, env.json), figures, and a copy of the code used for that report (`_code`) |

Working copies and preserved copies are kept apart. Preserved copies and past reports' `_code` folders are never edited.

## Method

The same workflow is run repeatedly under the same conditions through the ComfyUI API, recording time per image, sampling it/s, and peak VRAM / power / temperature.

- Standard prompt set v1: 3 prompts (landscape, still life, interior) × seeds 1001–1005
- The representative value is the median. A difference under 3% between two conditions is "no change", 3–5% is "borderline", and 5% or more is "changed"
- Each result has an `env.json` recording the GPU, driver, ComfyUI and PyTorch versions, and the sha256 of the script and workflow (from v1.1)

## Requirements

Check these before trying to reproduce. If any is missing, the measurement won't start or will stop partway.

**When using the measurement script (`frostlab_bench.py`)**

| Item | Requirement |
| --- | --- |
| GPU | An NVIDIA GPU and `nvidia-smi`. GPU info is read at startup, so without it the script stops immediately |
| ComfyUI | Must be running. Desktop, portable or manual install all work. The default address is `127.0.0.1:8188`; set `--server` if yours differs |
| Python | Run it with the Python that ComfyUI uses (it includes `aiohttp`). System Python may fail because it lacks `aiohttp` |
| Model | The checkpoint in the workflow, `v1-5-pruned-emaonly-fp16.safetensors`, must be in ComfyUI's `models/checkpoints` |
| OS | Measured on Windows. Not tested on other operating systems |

**Additional requirements when using the batch files (`run_*.bat`)**

- They assume **ComfyUI Desktop** for Windows. The batch files call `..\ComfyUI-Installs\ComfyUI\ComfyUI\.venv\Scripts\python.exe`.
- So this repository folder must sit directly under `%LOCALAPPDATA%\Comfy-Desktop`, next to the `ComfyUI-Installs` folder. Go to `%LOCALAPPDATA%\Comfy-Desktop` in a command prompt and run `git clone https://github.com/DedMoroZ-DOL/frostlab.git` to get it in that location.
- If you installed ComfyUI another way, change the `set PY=` line in the batch file to your ComfyUI Python path, or run the command below directly.
- The measurements used ComfyUI 0.45.5 (Comfy Desktop). The folder layout may differ between Desktop versions.

## Reproducing

1. Start ComfyUI. Use the repository's `sd15_api.json` as the workflow. To use your own workflow, save one with a single KSampler via Workflow → Export (API).
2. Run the measurement script with ComfyUI's Python. With ComfyUI Desktop and this repository in the location above, that is:

```
..\ComfyUI-Installs\ComfyUI\ComfyUI\.venv\Scripts\python.exe frostlab_bench.py --gpu-label 5070ti --workflow sd15_api.json --out "my_results\5070ti"
```

**Always point `--out` at a new folder.** The batch files in this repository and the commands in `run_versions` save results into the original results folders under `frostlab_results\Report NNN`, so running them as-is overwrites the original measurement results you downloaded.

| Argument | Default | Description |
| --- | --- | --- |
| `--gpu-label` | (required) | Label added to the result file names |
| `--workflow` | (required) | Workflow saved with Export (API) |
| `--mode` | `all` | `speed` (15-image speed test), `batch` (batch limits), `all` |
| `--batches` | `1,2,4,8` | List of batch sizes to measure |
| `--width`, `--height` | `512` | Measurement resolution (from v1.2) |
| `--out` | `frostlab_results` | Results folder |

Results depend on the GPU, driver, and ComfyUI / PyTorch versions. When comparing, also check the environment recorded in each results folder's `env.json`.

The exact commands used for each report are in `run_versions/README.md` (Korean).

## License

The code is under the [MIT License](LICENSE).
