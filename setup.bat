@echo off
py -3.11 -m venv .venv
call .venv\Scripts\activate
py -3.11 -m pip install --upgrade pip
pip install -r requirements.txt
echo Setup completed! 