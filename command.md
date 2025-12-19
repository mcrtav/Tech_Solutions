
python -m venv venv   
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass    
venv\Scripts\Activate 

deactivate -> desativar venv

py -m pip install -r requirements.txt
python manage.py makemigrations                         
python manage.py migrate
python manage.py seed_produtos


python manage.py runserver 8080

git add .
git commit -m "9º commit - OK"
git push -u origin main