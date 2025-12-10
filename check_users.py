#!/usr/bin/env python
"""Script para verificar usuarios existentes"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from rappiSafe.models import User, RepartidorProfile

print('='*50)
print('=== USUARIOS EXISTENTES ===')
print('='*50)
users = User.objects.all()
print(f'\nTotal usuarios: {users.count()}\n')

if users.count() > 0:
    for u in users[:20]:
        print(f'- Username: "{u.username}"')
        print(f'  Email: "{u.email}"')
        print(f'  Rol: {u.rol}')
        print(f'  Activo: {u.activo}')
        print(f'  ID: {u.id}')
        print()
else:
    print('No hay usuarios en la base de datos.\n')

print('='*50)
print('=== PERFILES DE REPARTIDOR ===')
print('='*50)
profiles = RepartidorProfile.objects.all()
print(f'\nTotal perfiles: {profiles.count()}\n')

if profiles.count() > 0:
    for p in profiles[:20]:
        print(f'- Usuario: "{p.user.username}"')
        print(f'  Número ID: "{p.numero_identificacion}"')
        print(f'  Estado: {p.estado}')
        print()
else:
    print('No hay perfiles de repartidor en la base de datos.\n')

print('='*50)
print('RESUMEN:')
print(f'- {users.count()} usuarios totales')
print(f'- {User.objects.filter(rol="repartidor").count()} repartidores')
print(f'- {User.objects.filter(rol="operador").count()} operadores')
print(f'- {User.objects.filter(rol="administrador").count()} administradores')
print(f'- {profiles.count()} perfiles de repartidor')
print('='*50)
