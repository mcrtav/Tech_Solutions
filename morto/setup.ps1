
# Creat o ambiente virtual
python -m venv venv

# Altera a política de execução para permitir a execução de scripts
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# Ativa o ambiente virtual
& venv\Scripts\Activate.ps1

# Instala as dependências
python -m pip install flask requests flask_cors flask_sqlalchemy
