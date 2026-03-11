#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
import re
import sys
import io

def translate_message(msg):
    """Translate commit message from Spanish to English"""
    # Ensure we're working with UTF-8
    if isinstance(msg, bytes):
        msg = msg.decode('utf-8', errors='replace')

    # Remove Co-Authored-By lines
    lines = msg.split('\n')
    lines = [line for line in lines if not line.strip().startswith('Co-Authored-By:')]

    # Translation dictionary
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

    # Translate first line if needed
    if lines:
        first_line = lines[0].strip()
        for spanish, english in translations.items():
            if first_line == spanish.strip():
                lines[0] = english
                break

    msg = '\n'.join(lines)

    # Spanish to English replacements in commit body
    body_replacements = [
        (r"Simplificado render\.yaml para usar SQLite", "Simplified render.yaml to use SQLite"),
        (r"Eliminadas dependencias de PostgreSQL", "Removed PostgreSQL dependencies"),
        (r"Actualizado settings\.py para usar solo SQLite", "Updated settings.py to use SQLite only"),
        (r"Configurado ALLOWED_HOSTS para Render", "Configured ALLOWED_HOSTS for Render"),
        (r"Agregado script create_superuser\.py", "Added create_superuser.py script"),
        (r"Usuario admin se crea autom.*?ticamente en cada deploy", "Admin user is created automatically on each deploy"),
        (r"Credenciales:", "Credentials:"),
        (r"El archivo static/css/input\.css no estaba en el repositorio porque", "The static/css/input.css file was not in the repository because"),
        (r"\.gitignore bloqueaba todo /static/\.", ".gitignore was blocking all /static/."),
        (r"Ahora se permite espec.*?ficamente", "Now it specifically allows"),
        (r"este archivo fuente mientras se siguen ignorando los archivos generados\.?", "this source file while still ignoring generated files"),
    ]

    for pattern, replacement in body_replacements:
        msg = re.sub(pattern, replacement, msg, flags=re.IGNORECASE | re.DOTALL)

    # Clean up extra whitespace
    msg = re.sub(r'\n{3,}', '\n\n', msg)
    return msg.strip()

def get_commit_list():
    """Get list of commits in reverse order (oldest first)"""
    result = subprocess.run(['git', 'log', '--reverse', '--format=%H'],
                          capture_output=True, text=True, check=True)
    return result.stdout.strip().split('\n')

def get_commit_info(commit_hash):
    """Get commit message and other info"""
    msg_result = subprocess.run(['git', 'log', '--format=%B', '-n', '1', commit_hash],
                               capture_output=True, text=True, check=True)
    return msg_result.stdout

def rewrite_commits():
    """Rewrite all commits with translated messages"""
    print("Getting commit list...")
    commits = get_commit_list()
    print(f"Found {len(commits)} commits")

    print("\nStarting rebase...")
    print("This will rewrite all commits from the root.")

    # Start rebase from root
    result = subprocess.run([
        'git', 'rebase', '--root', '-i', '--exec',
        'git commit --amend -F <(git log --format=%B -n 1 HEAD | python translate_commit.py)'
    ], shell=True, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False

    print("Done!")
    return True

if __name__ == '__main__':
    rewrite_commits()
