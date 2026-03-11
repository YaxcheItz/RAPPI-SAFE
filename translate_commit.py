#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import re
import io

# Ensure stdin is UTF-8
sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')

# Read commit message from stdin
msg = sys.stdin.read()

# Remove Co-Authored-By lines (remove Claude as contributor)
lines = msg.split('\n')
lines = [line for line in lines if not line.strip().startswith('Co-Authored-By:')]
msg = '\n'.join(lines).strip()

# Translation dictionary - Spanish to English
translations = {
    "Agregar compilación de TailwindCSS en build": "Add TailwindCSS compilation to build script",
    "Habilitar DEBUG temporalmente para diagnosticar error 500": "Enable DEBUG mode temporarily to diagnose 500 errors",
    "Fix create_superuser script con campos correctos del modelo": "Fix create_superuser script with correct model fields",
    "Fix ALLOWED_HOSTS y agregar creación automática de superusuario": "Fix ALLOWED_HOSTS and add automatic superuser creation",
    "Configurar RappiSafe para Render con SQLite": "Configure RappiSafe for Render deployment with SQLite",
    "📝 Se quitan comentarios": "Remove unnecessary comments",
    "Proyecto Final": "Add final project submission",
    "finales cambios": "Apply final changes and improvements",
    "final1": "Update to final version",
    "cambios alertas y mas admin y eso": "Update alerts system and admin panel",
    "🐛 Fix bigs": "Fix bugs",
    "ngrok": "Add ngrok configuration for mobile testing",
    "abajo": "Update layout and positioning",
    "telefono": "Add phone number field to user model",
    "mensajes telegram": "Add Telegram messaging integration",
    "agitacion": "Add shake detection feature for emergency alerts",
}

# Get first line (commit subject)
if lines:
    first_line = lines[0].strip()

    # Check if first line needs translation
    for spanish, english in translations.items():
        if first_line == spanish.strip():
            lines[0] = english
            break

    msg = '\n'.join(lines).strip()

# Spanish to English replacements in commit body
body_replacements = [
    (r"Simplificado render\.yaml para usar SQLite", "Simplified render.yaml to use SQLite"),
    (r"Eliminadas dependencias de PostgreSQL", "Removed PostgreSQL dependencies"),
    (r"Actualizado settings\.py para usar solo SQLite", "Updated settings.py to use SQLite only"),
    (r"Configurado ALLOWED_HOSTS para Render", "Configured ALLOWED_HOSTS for Render"),
    (r"Agregado script create_superuser\.py", "Added create_superuser.py script"),
    (r"Usuario admin se crea autom.*?ticamente en cada deploy", "Admin user is created automatically on each deploy"),
    (r"Credenciales:", "Credentials:"),
]

for pattern, replacement in body_replacements:
    msg = re.sub(pattern, replacement, msg, flags=re.IGNORECASE)

# Clean up extra whitespace
msg = re.sub(r'\n{3,}', '\n\n', msg)
msg = msg.strip()

print(msg)
