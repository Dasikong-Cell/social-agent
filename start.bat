@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ==============================================
echo       AI Copywriter Agent Backend
echo ==============================================
echo.
echo Starting backend... Do NOT close this window.
echo URL: http://127.0.0.1:8000
echo.
"%USERPROFILE%\AppData\Roaming\TRAE SOLO CN\ModularData\ai-agent\vm\tools\python\python.exe" main_server.py
echo.
echo Server stopped. Press any key to exit...
pause >nul