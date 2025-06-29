@echo off
echo --- Instalando dependencias de Python (Backend) ---

REM Asumimos que Python y pip estan en el PATH.
REM Es recomendable estar en un entorno virtual de Python antes de ejecutar esto.
pip install -r requirements.txt
pip install djangorestframework>=3.14,<3.16
pip install django-cors-headers

echo.
echo --- Instalando dependencias de Node.js (Frontend) ---

REM Asumimos que Node.js y npm estan en el PATH.
cd frontend
npm install

cd ..
echo.
echo --- Instalacion completada ---
echo.
echo RECUERDA:
echo 1. Activar tu entorno virtual de Python si aun no lo has hecho.
echo 2. Configurar 'corsheaders' en settings.py (INSTALLED_APPS, MIDDLEWARE, y CORS_ALLOW_ALL_ORIGINS = True para desarrollo).
echo 3. Ejecutar migraciones de Django: python school_management_system/manage.py migrate
echo 4. Para iniciar:
echo    - Backend (Django): python school_management_system/manage.py runserver
echo    - Frontend (React): cd frontend && npm start
pause
