python -m venv venv

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass


venv\Scripts\Activate

python -m pip install flask requests flask_cors flask_sqlalchemy
