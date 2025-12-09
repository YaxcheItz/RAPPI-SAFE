# Inicio Rápido - Rappi Safe

Esta guía te ayudará a tener Rappi Safe funcionando en menos de 10 minutos.

## Requisitos

- Python 3.10+
- Node.js 18+
- npm

## Instalación Rápida

### 1. Instalar Dependencias Python

```bash
pip install -r requirements.txt
```

### 2. Instalar Node.js y Compilar CSS

```bash
npm install
npm run build:css
```

### 3. Inicializar Base de Datos

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Crear Datos de Prueba

```bash
python manage.py init_demo_data
```

Este comando creará automáticamente:
- 1 Superusuario (admin/admin123)
- 3 Repartidores (repartidor1, repartidor2, repartidor3 / test123)
- 2 Operadores (operador1, operador2 / test123)
- 1 Administrador (admin1 / test123)
- Contactos de confianza para cada repartidor
- 3 Zonas de riesgo de ejemplo

### 5. Ejecutar el Servidor

**Con WebSockets (Recomendado):**
```bash
daphne -b 0.0.0.0 -p 8000 mysite.asgi:application
```

**O sin WebSockets:**
```bash
python manage.py runserver
```

### 6. Acceder a la Aplicación

Abre tu navegador en: `http://localhost:8000`

## Usuarios de Prueba

| Usuario | Contraseña | Rol |
|---------|-----------|-----|
| admin | admin123 | Superusuario |
| repartidor1 | test123 | Repartidor |
| repartidor2 | test123 | Repartidor |
| repartidor3 | test123 | Repartidor |
| operador1 | test123 | Operador |
| operador2 | test123 | Operador |
| admin1 | test123 | Administrador |

## Probar las Funcionalidades

### Como Repartidor

1. Accede con: `repartidor1` / `test123`
2. Verás el botón de pánico en la pantalla principal
3. Mantén presionado 3 segundos para activar
4. Acepta los permisos de ubicación cuando el navegador lo solicite
5. Explora:
   - Contactos de confianza
   - Solicitud de ayuda psicológica

### Como Operador

1. Accede con: `operador1` / `test123`
2. Verás el dashboard de monitoreo
3. Si hay alertas activas, las verás en el mapa y la lista
4. Haz clic en una alerta para ver detalles
5. Prueba:
   - Atender alerta
   - Agregar notas a la bitácora
   - Registrar folio 911
   - Cerrar alerta

### Como Administrador

1. Accede con: `admin1` / `test123`
2. Verás estadísticas generales
3. Explora:
   - Gestión de usuarios
   - Estadísticas y reportes
   - Django Admin (http://localhost:8000/admin/)

## Desarrollo

### Modo Watch para CSS

Si estás desarrollando y modificando estilos:

```bash
npm run watch:css
```

Esto recompilará automáticamente el CSS cada vez que guardes cambios en `static/css/input.css` o en los templates.

### Shell de Django

Para experimentar con los modelos:

```bash
python manage.py shell
```

```python
from rappiSafe.models import *

# Ver todos los repartidores
User.objects.filter(rol='repartidor')

# Ver alertas activas
Alerta.objects.filter(estado__in=['pendiente', 'en_atencion'])

# Crear una alerta de prueba
repartidor = User.objects.get(username='repartidor1')
alerta = Alerta.objects.create(
    repartidor=repartidor,
    tipo='panico',
    latitud=19.4326,
    longitud=-99.1332,
    nivel_bateria=75
)
```

## Resolución de Problemas

### Error: "No module named 'channels'"

```bash
pip install -r requirements.txt
```

### Error: "npm: command not found"

Instala Node.js desde: https://nodejs.org/

### Error: El CSS no se aplica

```bash
npm run build:css
```

Luego recarga la página con Ctrl+F5 (hard reload).

### WebSockets no funcionan

Asegúrate de estar usando Daphne:

```bash
daphne -b 0.0.0.0 -p 8000 mysite.asgi:application
```

### La geolocalización no funciona

- **Chrome**: Funciona en localhost sin HTTPS
- **Firefox**: Funciona en localhost sin HTTPS
- **Safari**: Puede requerir HTTPS incluso en desarrollo

Si es necesario, usa HTTPS en desarrollo o prueba en un dispositivo móvil real.

## Siguientes Pasos

1. Lee el [README.md](README.md) completo para entender todas las funcionalidades
2. Explora el código en `rappiSafe/models.py` para ver la estructura de datos
3. Revisa las vistas en `rappiSafe/views.py`
4. Modifica los templates en `rappiSafe/templates/`
5. Personaliza los estilos en `static/css/input.css`

## Soporte

Si encuentras algún problema:

1. Verifica que todos los pasos de instalación se completaron
2. Revisa la consola del navegador (F12) para errores JavaScript
3. Revisa la consola del servidor para errores de Django
4. Consulta la documentación completa en README.md

¡Disfruta usando Rappi Safe!
