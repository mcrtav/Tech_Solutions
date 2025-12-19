
python -m venv venv   
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass    
venv\Scripts\Activate 

deactivate -> desativar venv

py -m pip install -r requirements.txt
python manage.py makemigrations                         
python manage.py migrate
python manage.py seed_produtos


python manage.py runserver 808