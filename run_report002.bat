@echo off
cd /d "%~dp0"
set PY=..\ComfyUI-Installs\ComfyUI\ComfyUI\.venv\Scripts\python.exe
set WF=sd15_api.json
set R2=frostlab_results\Report 002
set R3=frostlab_results\Report 003

echo ================================================
echo  Frost Lab Report 002 + 003 - resolution, SD1.5, RTX 5070 Ti
echo  bench v1.2 / speed mode only / 9 runs
echo  002: square size 512, 768, 1024, 1536
echo  003: same pixel count, aspect ratio 3:2, 16:9, 21:9, 9:16
echo  (512x512 is the shared baseline for both reports)
echo ------------------------------------------------
echo  Check first: ComfyUI running / only Claude app open / 2 monitors
echo               Ryzen Master Default / NVIDIA app auto-tune OFF
echo               No ComfyUI or driver update since Report 001
echo  Reproducing? Change R2 and R3 above to NEW folders,
echo               otherwise the original results are overwritten.
echo ================================================
pause

echo.
echo [1/9] 512x512 (shared baseline)
%PY% frostlab_bench.py --gpu-label 5070ti_512x512 --mode speed --width 512 --height 512 --workflow %WF% --out "%R2%\5070ti_512x512"
if errorlevel 1 goto fail

echo.
echo [2/9] 768x768
%PY% frostlab_bench.py --gpu-label 5070ti_768x768 --mode speed --width 768 --height 768 --workflow %WF% --out "%R2%\5070ti_768x768"
if errorlevel 1 goto fail

echo.
echo [3/9] 1024x1024
%PY% frostlab_bench.py --gpu-label 5070ti_1024x1024 --mode speed --width 1024 --height 1024 --workflow %WF% --out "%R2%\5070ti_1024x1024"
if errorlevel 1 goto fail

echo.
echo [4/9] 1536x1536
%PY% frostlab_bench.py --gpu-label 5070ti_1536x1536 --mode speed --width 1536 --height 1536 --workflow %WF% --out "%R2%\5070ti_1536x1536"
if errorlevel 1 goto fail

echo.
echo [5/9] 624x416 (3:2)
%PY% frostlab_bench.py --gpu-label 5070ti_624x416 --mode speed --width 624 --height 416 --workflow %WF% --out "%R3%\5070ti_624x416"
if errorlevel 1 goto fail

echo.
echo [6/9] 688x384 (16:9)
%PY% frostlab_bench.py --gpu-label 5070ti_688x384 --mode speed --width 688 --height 384 --workflow %WF% --out "%R3%\5070ti_688x384"
if errorlevel 1 goto fail

echo.
echo [7/9] 784x336 (21:9)
%PY% frostlab_bench.py --gpu-label 5070ti_784x336 --mode speed --width 784 --height 336 --workflow %WF% --out "%R3%\5070ti_784x336"
if errorlevel 1 goto fail

echo.
echo [8/9] 384x688 (9:16)
%PY% frostlab_bench.py --gpu-label 5070ti_384x688 --mode speed --width 384 --height 688 --workflow %WF% --out "%R3%\5070ti_384x688"
if errorlevel 1 goto fail

echo.
echo [9/9] 512x512 again (end-of-day drift check)
%PY% frostlab_bench.py --gpu-label 5070ti_512x512_end --mode speed --width 512 --height 512 --workflow %WF% --out "%R2%\5070ti_512x512_end"
if errorlevel 1 goto fail

echo.
echo All done. Results: %R2% and %R3%
pause
exit /b 0

:fail
echo.
echo Error during measurement. Check the message above.
pause
exit /b 1
