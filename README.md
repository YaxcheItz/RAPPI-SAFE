# Rappi Safe

Sistema integral de seguridad para repartidores con botón de pánico, geolocalización en tiempo real, detección de accidentes y monitoreo centralizado.

## Características Principales

### Para Repartidores (Plataforma Móvil Web)
- **Botón de Pánico**: Activación mediante pulsación prolongada de 3 segundos
- **Geolocalización en Tiempo Real**: Envío automático de ubicación cada 5 segundos durante alertas
- **Contactos de Confianza**: Hasta 3 contactos que son notificados automáticamente en emergencias
- **Solicitud de Ayuda Psicológica**: Canal confidencial para apoyo profesional
- **Interfaz Mobile-First**: Diseño 100% responsive optimizado para dispositivos móviles

### Para Operadores (Centro de Monitoreo)
- **Dashboard de Monitoreo en Tiempo Real**: WebSockets para actualizaciones instantáneas (< 5s)
- **Mapa Interactivo**: Visualización de alertas activas con Leaflet.js
- **Seguimiento de Trayectorias**: Visualización del recorrido del repartidor durante emergencias
- **Gestión de Incidentes**: Sistema completo de bitácora y seguimiento
- **Notificaciones Sonoras y Visuales**: Alertas inmediatas de nuevos incidentes
- **Acceso a Contactos de Confianza**: Información para notificación rápida

### Para Administradores
- **Gestión de Usuarios**: CRUD completo con roles y permisos
- **Estadísticas Avanzadas**: Reportes por período, tipo de alerta y zona
- **Zonas de Riesgo**: Identificación de áreas con mayor incidencia
- **Panel de Django Admin**: Acceso completo a la administración del sistema

## Tecnologías Utilizadas

### Backend
- **Django 5.2.8**: Framework web principal
- **Django Channels 4.0**: WebSockets para tiempo real
- **SQLite**: Base de datos (fácilmente migrable a PostgreSQL)
- **Python 3.10+**: Lenguaje de programación

### Frontend
- **Django Templates**: Sistema de plantillas nativo
- **TailwindCSS**: Framework CSS con color principal #dc2626
- **Leaflet.js**: Mapas interactivos
- **Font Awesome**: Iconos
- **Vanilla JavaScript**: Sin frameworks SPA

### Características Técnicas
- **WebSockets**: Comunicación bidireccional en tiempo real
- **Geolocation API**: Acceso al GPS del dispositivo
- **Device Motion API**: Detección de movimientos bruscos (preparado para futura implementación)
- **Battery API**: Monitoreo del nivel de batería
- **Notifications API**: Notificaciones del navegador

## Instalación

### Requisitos Previos
- Python 3.10 o superior
- Node.js 18+ y npm (para TailwindCSS)
- Git

### Paso 1: Clonar el Repositorio
```bash
git clone <url-del-repositorio>
cd RappiSafe
```

### Paso 2: Crear Entorno Virtual
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Paso 3: Instalar Dependencias de Python
```bash
pip install -r requirements.txt
```

### Paso 4: Instalar Dependencias de Node.js y Compilar TailwindCSS
```bash
# Instalar dependencias
npm install

# Compilar CSS (modo desarrollo con watch)
npm run watch:css

# O compilar CSS una vez (producción)
npm run build:css
```

### Paso 5: Crear Base de Datos y Migraciones
```bash
python manage.py makemigrations
python manage.py migrate
```

### Paso 6: Crear Superusuario
```bash
python manage.py createsuperuser
```

### Paso 7: Crear Datos de Prueba (Opcional)
Puedes crear usuarios de prueba manualmente desde el Django Admin o usando la consola:

```python
python manage.py shell

from rappiSafe.models import User

# Crear repartidor
rep = User.objects.create_user(
    username='repartidor1',
    email='repartidor@test.com',
    password='test123',
    first_name='Juan',
    last_name='Pérez',
    rol='repartidor',
    telefono='+5215512345678'
)

# Crear operador
op = User.objects.create_user(
    username='operador1',
    email='operador@test.com',
    password='test123',
    first_name='María',
    last_name='González',
    rol='operador'
)

# Crear administrador
admin = User.objects.create_user(
    username='admin1',
    email='admin@test.com',
    password='test123',
    first_name='Carlos',
    last_name='Admin',
    rol='administrador',
    is_staff=True
)
```

### Paso 8: Ejecutar el Servidor
```bash
# Servidor de desarrollo con Daphne (para WebSockets)
daphne -b 0.0.0.0 -p 8000 mysite.asgi:application

# O servidor de desarrollo estándar (sin WebSockets en tiempo real)
python manage.py runserver
```

La aplicación estará disponible en: `http://localhost:8000`

## Usuarios de Prueba

Después de crear los usuarios de prueba, puedes acceder con:

- **Repartidor**: username: `repartidor1`, password: `test123`
- **Operador**: username: `operador1`, password: `test123`
- **Administrador**: username: `admin1`, password: `test123`

## Estructura del Proyecto

```
RappiSafe/
├── mysite/                 # Configuración del proyecto Django
│   ├── settings.py         # Configuración principal
│   ├── asgi.py            # Configuración ASGI para WebSockets
│   ├── urls.py            # URLs principales
│   └── wsgi.py            # Configuración WSGI
├── rappiSafe/             # Aplicación principal
│   ├── models.py          # Modelos de base de datos
│   ├── views.py           # Vistas del sistema
│   ├── urls.py            # URLs de la aplicación
│   ├── admin.py           # Configuración del Django Admin
│   ├── consumers.py       # Consumers de WebSockets
│   ├── routing.py         # Routing de WebSockets
│   ├── utils.py           # Funciones utilitarias
│   ├── signals.py         # Signals de Django
│   └── templates/         # Templates HTML
│       ├── rappiSafe/
│       │   ├── base.html
│       │   ├── repartidor/
│       │   ├── operador/
│       │   └── admin/
│       └── registration/
│           └── login.html
├── static/                # Archivos estáticos globales
│   ├── css/
│   │   ├── input.css      # CSS de entrada para Tailwind
│   │   └── output.css     # CSS compilado
│   └── js/
├── media/                 # Archivos subidos por usuarios
├── requirements.txt       # Dependencias Python
├── package.json          # Dependencias Node.js
├── tailwind.config.js    # Configuración de TailwindCSS
├── manage.py             # CLI de Django
└── README.md             # Este archivo
```

## Modelos de Base de Datos

### User (Usuario Extendido)
- Roles: repartidor, operador, administrador
- Email único
- Estado activo/inactivo

### RepartidorProfile
- Perfil extendido del repartidor
- Ubicación en tiempo real
- Nivel de batería
- Estado (disponible, en_ruta, emergencia, offline)

### Alerta
- ID UUID
- Tipo: pánico o accidente detectado
- Estado: pendiente, en_atención, atendida, cerrada, falsa_alarma
- Ubicación (lat/lon)
- Nivel de batería
- Datos de sensores

### Trayectoria
- Puntos de ubicación durante una alerta
- Timestamp de cada punto

### ContactoConfianza
- Hasta 3 contactos por repartidor
- Nombre, teléfono, relación
- Estado de validación

### Incidente
- Asociado a una alerta
- Operador asignado
- Folio 911
- Bitácora de acciones
- Tiempo de respuesta

### Bitacora
- Registro de acciones durante incidente
- Operador que realizó la acción
- Timestamp

### EstadisticaRiesgo
- Zonas geográficas
- Puntuación de riesgo (0-100)
- Conteo de alertas por tipo

### SolicitudAyudaPsicologica
- Solicitudes confidenciales
- Nivel de urgencia (1-10)
- Estado de atención

### RutaSegura
- Comparación ruta rápida vs segura
- Puntuaciones de riesgo
- Selección del repartidor

## Funcionalidades Implementadas

### ✅ Completadas
1. Sistema de autenticación con roles
2. Botón de pánico con activación de 3 segundos
3. Geolocalización en tiempo real
4. WebSockets para tiempo real (< 5s)
5. Dashboard de monitoreo para operadores
6. Mapa interactivo con Leaflet.js
7. Sistema de gestión de incidentes y bitácora
8. Contactos de confianza (hasta 3)
9. Solicitud de ayuda psicológica
10. Panel de administración
11. Estadísticas y reportes
12. Notificaciones del navegador
13. Diseño responsive mobile-first
14. Actualización de batería automática

### 🚧 Pendientes (Mejoras Futuras)
1. Detección automática de accidentes con acelerómetro/giroscopio
2. Cálculo de rutas seguras vs rápidas
3. Funcionalidad offline completa con Service Workers
4. Generación de reportes PDF
5. Notificaciones SMS a contactos de confianza
6. Modo PWA (Progressive Web App)
7. Integración con APIs de mapas para cálculo de rutas
8. Dashboard de estadísticas con gráficas avanzadas

## Uso del Sistema

### Como Repartidor

1. **Login**: Accede con tus credenciales
2. **Pantalla Principal**: Verás el botón de pánico y tu estado actual
3. **Activar Pánico**: Mantén presionado el botón rojo por 3 segundos
4. **Durante Alerta**: Tu ubicación se envía automáticamente cada 5 segundos
5. **Cancelar**: Puedes cancelar una alerta si fue activada por error
6. **Contactos**: Gestiona hasta 3 contactos de confianza
7. **Ayuda**: Solicita apoyo psicológico cuando lo necesites

### Como Operador

1. **Login**: Accede con tus credenciales
2. **Dashboard**: Visualiza todas las alertas activas en tiempo real
3. **Mapa**: Ve la ubicación de todos los repartidores con alertas activas
4. **Atender**: Haz clic en "Atender Alerta" para tomar un caso
5. **Seguimiento**: Ve la trayectoria en tiempo real
6. **Contactar**: Llama al repartidor o a sus contactos de confianza
7. **Bitácora**: Registra todas las acciones realizadas
8. **911**: Ingresa el folio si contactas a autoridades
9. **Cerrar**: Marca el incidente como cerrado cuando se resuelva

### Como Administrador

1. **Login**: Accede con tus credenciales
2. **Dashboard**: Ve estadísticas generales del sistema
3. **Usuarios**: Gestiona repartidores, operadores y otros admins
4. **Estadísticas**: Consulta reportes por período y tipo
5. **Django Admin**: Acceso completo a todos los modelos

## Seguridad

- Autenticación obligatoria para todas las rutas
- Verificación de roles para cada vista
- CSRF protection habilitado
- WebSockets con autenticación
- Sesiones de 24 horas con renovación automática
- Passwords hasheados con algoritmos seguros de Django

## Comandos Útiles

```bash
# Compilar CSS de Tailwind
npm run build:css

# Modo watch para desarrollo
npm run watch:css

# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Ejecutar servidor de desarrollo
python manage.py runserver

# Ejecutar servidor con WebSockets (Daphne)
daphne -b 0.0.0.0 -p 8000 mysite.asgi:application

# Recopilar archivos estáticos
python manage.py collectstatic

# Shell de Django
python manage.py shell
```

## Deployment

### Consideraciones para Producción

1. **Cambiar SECRET_KEY**: Generar una nueva clave secreta
2. **DEBUG = False**: Desactivar modo debug
3. **ALLOWED_HOSTS**: Configurar dominios permitidos
4. **Base de Datos**: Migrar a PostgreSQL
5. **Redis**: Usar Redis para Channels Layer en lugar de InMemory
6. **HTTPS**: Obligatorio para Geolocation API
7. **Static Files**: Configurar servidor web (Nginx) para servir archivos estáticos
8. **ASGI Server**: Usar Daphne o Uvicorn con supervisor/systemd

### Ejemplo de Configuración para Producción

```python
# settings.py
import os

DEBUG = False
ALLOWED_HOSTS = ['tudominio.com', 'www.tudominio.com']

# Base de datos
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': '5432',
    }
}

# Channels Layer con Redis
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [(os.environ.get('REDIS_HOST', 'localhost'), 6379)],
        },
    },
}

# Seguridad
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

## Soporte y Contacto

Para reportar problemas o solicitar nuevas funcionalidades, por favor crea un issue en el repositorio.

## Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

## Créditos

Desarrollado con Django, TailwindCSS y mucho café.

---

**Rappi Safe** - Sistema de Seguridad para Repartidores
