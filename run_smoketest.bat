@echo off
cd /d "%~dp0"
set PY=..\ComfyUI-Installs\ComfyUI\ComfyUI\.venv\Scripts\python.exe

echo ================================================
echo  Frost Lab smoke test - bench v1.2, 624x416, batch 1 only
echo  Checks that --width/--height work before the real run.
echo  Results go to frostlab_results\_smoketest (not published)
echo ================================================
pause

%PY% frostlab_bench.py --gpu-label smoketest --mode batch --batches 1 --width 624 --height 416 --workflow sd15_api.json --out "frostlab_results\_smoketest"
if errorlevel 1 goto fail

echo.
echo Done. Open frostlab_results\_smoketest\env.json and check:
echo   bench_version = 1.2 / resolution = 624x416
echo   (workflow_resolution 512x512 and the size warning are expected)
echo   Image in ComfyUI output\frostlab\smoketest is 624 x 416.
pause
exit /b 0

:fail
echo.
echo Error. Check the message above.
pause
exit /b 1
