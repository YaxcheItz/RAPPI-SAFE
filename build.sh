#!/usr/bin/env bash
# exit on error
set -o errexit

# Instalar dependencias Python
pip install --upgrade pip
pip install -r requirements.txt

# Instalar Node.js dependencies y compilar TailwindCSS
npm install
npm run build:css

# Recolectar archivos estáticos
python manage.py collectstatic --no-input

# Migrar base de datos
python manage.py migrate

# Crear usuarios y datos de demostración
python manage.py init_demo_data
