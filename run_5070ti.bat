@echo off
cd /d "%~dp0"
set PY=..\ComfyUI-Installs\ComfyUI\ComfyUI\.venv\Scripts\python.exe

echo ================================================
echo  Frost Lab Report 001 - RTX 5070 Ti benchmark
echo  Check first: ComfyUI running / only Claude app open / 2 monitors
echo               Ryzen Master Default / NVIDIA app auto-tune OFF
echo ================================================
pause

echo.
echo [1/2] Basic: speed 15 images + batch 1,2,4,8
%PY% frostlab_bench.py --gpu-label 5070ti --workflow sd15_api.json --out "frostlab_results\Report 001\5070ti_basic"
if errorlevel 1 goto fail

echo.
echo [2/2] Limit: batch 16,32,64
%PY% frostlab_bench.py --gpu-label 5070tix --mode batch --batches 16,32,64 --workflow sd15_api.json --out "frostlab_results\Report 001\5070ti_limit"
if errorlevel 1 goto fail

echo.
echo All done. Results: frostlab_results\Report 001\5070ti_basic and 5070ti_limit
pause
exit /b 0

:fail
echo.
echo Error during measurement. Check the message above.
pause
exit /b 1
