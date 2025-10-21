@echo off
echo.
echo ========================================
echo   Graph-Based AI Agent
echo   Subtitle Improvement
echo ========================================
echo.
echo Config: 7 max iterations, 95%% threshold
echo.

cd /d "D:\video-agent"
call venv\Scripts\activate.bat

cd agent

python auto_improve_subtitles.py

echo.
echo ========================================
echo   Check: agent\output\
echo ========================================
echo.
pause
