#!/usr/bin/env python
"""Script para crear un superusuario automáticamente en deploy"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Credenciales por defecto (puedes cambiarlas)
username = 'admin'
email = 'admin@rappisafe.com'
password = 'admin123'  # CAMBIA ESTO en producción real

if not User.objects.filter(username=username).exists():
    user = User.objects.create_superuser(
        username=username,
        email=email,
        password=password,
        first_name='Admin',
        last_name='RappiSafe',
        telefono='+525555555555',
        rol='administrador'
    )
    print(f'✅ Superusuario creado: {username}')
else:
    print(f'ℹ️  Superusuario ya existe: {username}')
