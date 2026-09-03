@echo off
cd /d "%~dp0"
py -3 "%~dp0SuccubusVIPManager.py"
if errorlevel 1 pause
