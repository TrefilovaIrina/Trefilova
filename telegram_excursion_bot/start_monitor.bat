@echo off
cd /d %~dp0
:start
python bot.py
timeout /t 5
goto start 