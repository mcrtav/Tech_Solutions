echo off
python -m venv venv
call Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
call venv\Scripts\activate
python -m pip install flask requests flask_cors flask_sqlalchemy