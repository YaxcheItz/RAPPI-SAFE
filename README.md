<div align="center">

# 🚨 RappiSafe

### Sistema Integral de Seguridad para Repartidores

*Botón de pánico · Geolocalización en tiempo real · Monitoreo centralizado*

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Django](https://img.shields.io/badge/Django-5.2.8-green.svg)](https://www.djangoproject.com/)
[![Channels](https://img.shields.io/badge/Channels-4.0-orange.svg)](https://channels.readthedocs.io/)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.0-38B2AC.svg)](https://tailwindcss.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[Características](#-características-principales) ·
[Instalación](#-instalación-rápida) ·
[Cómo Probar](#-cómo-probar-el-sistema) ·
[Documentación](#-documentación)

</div>

---

## 📋 Tabla de Contenidos

- [Características Principales](#-características-principales)
- [Tecnologías](#-tecnologías-utilizadas)
- [Instalación Rápida](#-instalación-rápida)
- [Cómo Probar el Sistema](#-cómo-probar-el-sistema)
- [Uso con Dispositivos Móviles (ngrok)](#-uso-con-dispositivos-móviles)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Comandos Útiles](#-comandos-útiles)
- [Solución de Problemas](#-solución-de-problemas)
- [Documentación](#-documentación)
- [Licencia](#-licencia)

---

## 🎯 Características Principales

### 📱 Para Repartidores (Plataforma Móvil Web)
- **Botón de Pánico**: Activación mediante pulsación prolongada de 3 segundos
- **Geolocalización en Tiempo Real**: Envío automático de ubicación cada 5 segundos durante alertas
- **Contactos de Confianza**: Hasta 3 contactos que son notificados automáticamente en emergencias
- **Solicitud de Ayuda Psicológica**: Canal confidencial para apoyo profesional
- **Interfaz Mobile-First**: Diseño 100% responsive optimizado para dispositivos móviles

### 🖥️ Para Operadores (Centro de Monitoreo)
- **Dashboard de Monitoreo en Tiempo Real**: WebSockets para actualizaciones instantáneas (< 5s)
- **Mapa Interactivo**: Visualización de alertas activas con Leaflet.js
- **Seguimiento de Trayectorias**: Visualización del recorrido del repartidor durante emergencias
- **Gestión de Incidentes**: Sistema completo de bitácora y seguimiento
- **Notificaciones Sonoras y Visuales**: Alertas inmediatas de nuevos incidentes
- **Acceso a Contactos de Confianza**: Información para notificación rápida

### 👨‍💼 Para Administradores
- **Gestión de Usuarios**: CRUD completo con roles y permisos
- **Estadísticas Avanzadas**: Reportes por período, tipo de alerta y zona
- **Zonas de Riesgo**: Identificación de áreas con mayor incidencia
- **Panel de Django Admin**: Acceso completo a la administración del sistema

## 🛠️ Tecnologías Utilizadas

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

## 🚀 Instalación Rápida

### 📦 Requisitos Previos
- Python 3.10 o superior
- Node.js 18+ y npm (para TailwindCSS)
- Git

### ⚡ Quick Start (TL;DR)

```bash
# Clonar y entrar al proyecto
git clone <url-del-repositorio>
cd RappiSafe

# Configurar entorno virtual (Windows)
python -m venv venv
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
npm install

# Configurar base de datos
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Compilar CSS
npm run build:css

# Iniciar servidor
daphne -b 0.0.0.0 -p 8000 mysite.asgi:application

# Visitar: http://localhost:8000
```

### 📝 Instalación Detallada

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

## 👤 Usuarios de Prueba

Después de crear los usuarios de prueba, puedes acceder con:

| Rol | Username | Password | Acceso |
|-----|----------|----------|---------|
| 📱 Repartidor | `repartidor1` | `test123` | http://localhost:8000/repartidor/ |
| 🖥️ Operador | `operador1` | `test123` | http://localhost:8000/operador/ |
| 👨‍💼 Administrador | `admin1` | `test123` | http://localhost:8000/admin-dashboard/ |

---

## 🧪 Cómo Probar el Sistema

Esta sección te guiará para probar todas las funcionalidades del sistema.

### Escenario 1: Alerta de Pánico Completa (Lo Más Importante)

Este es el flujo principal del sistema. Te recomendamos probarlo primero.

#### 🎬 Preparación

1. **Abrir dos navegadores o ventanas**:
   - **Navegador/Ventana 1**: Repartidor (dispositivo móvil o simulación)
   - **Navegador/Ventana 2**: Operador (computadora)

2. **Iniciar sesión en ambos**:
   - Ventana 1: Login como `repartidor1`
   - Ventana 2: Login como `operador1`

#### 📱 Paso 1: Configurar Repartidor

1. **Login como repartidor1** → http://localhost:8000/accounts/login/
2. Acepta permisos de:
   - ✅ Ubicación/GPS
   - ✅ Notificaciones
3. Verás el **Dashboard del Repartidor** con:
   - Botón de pánico grande y rojo
   - Tu estado actual: "Disponible"
   - Nivel de batería
   - Menú de navegación

#### 🖥️ Paso 2: Preparar Operador

1. **Login como operador1** → http://localhost:8000/accounts/login/
2. Verás el **Dashboard de Monitoreo** con:
   - Lista de alertas activas (vacía inicialmente)
   - Contador de alertas pendientes
   - Mapa de alertas
3. Deja esta ventana abierta y visible

#### 🚨 Paso 3: Activar Alerta de Pánico

1. **En la ventana del repartidor**:
   - Mantén presionado el **botón rojo de pánico**
   - Verás una barra de progreso llenarse durante 3 segundos
   - NO lo sueltes hasta que se active

2. **Al activarse (después de 3 segundos)**:
   - ✅ Verás mensaje: "Alerta enviada"
   - ✅ El botón cambia a "Alerta Activa"
   - ✅ Aparece botón "Cancelar Alerta"
   - ✅ Tu ubicación se enviará cada 5 segundos

#### 👀 Paso 4: Observar en Dashboard del Operador

**Instantáneamente (< 5 segundos) en la ventana del operador verás**:

1. **Notificación del navegador** 🔔:
   ```
   🚨 Nueva Alerta de Emergencia
   Juan Pérez activó botón de pánico
   ```

2. **Sonido de alerta** 🔊 (opcional, según configuración)

3. **Nueva tarjeta de alerta** en el dashboard:
   ```
   ┌──────────────────────────────────────┐
   │ 🚨 Juan Pérez - PÁNICO               │
   │ 📍 [Tu ubicación actual]             │
   │ 🔋 67% batería                       │
   │ ⏰ Hace 5 segundos                   │
   │                                      │
   │ [Atender Alerta]  [Ver en Mapa]     │
   └──────────────────────────────────────┘
   ```

4. **Marcador rojo en el mapa** 📍 mostrando la ubicación del repartidor

#### 🎯 Paso 5: Atender la Alerta

1. **En el dashboard del operador**, haz clic en **"Atender Alerta"**

2. Serás redirigido a la **Vista de Monitoreo** que muestra:
   - **Mapa grande** con ubicación del repartidor
   - **Trayectoria en tiempo real** (línea roja)
   - **Panel de información**:
     ```
     Repartidor: Juan Pérez
     Teléfono: +52 55 1234 5678
     Batería: 67%
     Estado: En emergencia
     ```
   - **Contactos de confianza** (si los tiene configurados)
   - **Bitácora de acciones**

3. **Observa el mapa actualizarse cada 5 segundos** ⏱️:
   - El marcador se mueve en tiempo real
   - La línea roja (trayectoria) se extiende
   - Puedes hacer zoom in/out

#### 📝 Paso 6: Documentar Acciones

1. En el panel de **Bitácora**, agrega acciones:
   ```
   Ejemplo:
   "Llamé al repartidor, reporta que está siendo asaltado"
   [Agregar Acción]
   ```

2. Si llamaste al 911, ingresa el folio:
   ```
   Folio 911: 123456789
   [Guardar]
   ```

#### ✅ Paso 7: Cerrar el Incidente

1. Cuando la emergencia se resuelva, en la vista de monitoreo:
   - Selecciona el **estado final**:
     - ✅ Atendida (emergencia real resuelta)
     - ⚠️ Falsa Alarma
     - ❌ Cerrada (otras razones)
   - Agrega **descripción final**
   - Haz clic en **"Cerrar Incidente"**

2. **Resultados**:
   - La alerta desaparece del dashboard
   - El repartidor vuelve a estado "Disponible"
   - Se registra el tiempo de respuesta
   - Se actualiza en estadísticas

---

### Escenario 2: Configurar Contactos de Confianza

#### 📱 Como Repartidor

1. Login como `repartidor1`
2. Ve a **"Mis Contactos"** en el menú
3. Haz clic en **"Agregar Contacto"**
4. Llena el formulario:
   ```
   Nombre: María Pérez
   Teléfono: +52 55 8765 4321
   Relación: Esposa
   ```
5. Guarda y repite hasta tener 3 contactos máximo

#### 🖥️ Verificación (Como Operador)

1. Activa una alerta como repartidor
2. Como operador, atiende la alerta
3. En la vista de monitoreo, verás:
   ```
   📞 Contactos de Confianza:

   1. María Pérez (Esposa)
      Tel: +52 55 8765 4321
      [Llamar]

   2. [Otros contactos...]
   ```

---

### Escenario 3: Cancelar Alerta (Falsa Alarma)

#### 📱 Como Repartidor

1. Activa una alerta de pánico (mantén 3 segundos)
2. Inmediatamente haz clic en **"Cancelar Alerta"**
3. Confirma la cancelación

#### 🖥️ Verificación (Como Operador)

- La alerta aparecerá brevemente
- Cambiará automáticamente a estado "Falsa Alarma"
- Se moverá a la sección de alertas cerradas

---

### Escenario 4: Gestión de Usuarios (Como Administrador)

1. Login como `admin1` → http://localhost:8000/admin-dashboard/
2. Ve a **"Gestionar Usuarios"**
3. Prueba:
   - ➕ Crear nuevo usuario
   - ✏️ Editar usuario existente
   - 🔒 Desactivar usuario
   - 👁️ Ver detalles de usuario

---

### Escenario 5: Ver Estadísticas

#### 👨‍💼 Como Administrador

1. Login como `admin1`
2. En el **Dashboard Administrativo** verás:
   - 📊 Total de alertas por tipo
   - 📈 Alertas por período (día/semana/mes)
   - 🗺️ Mapa de calor con zonas de riesgo
   - ⏱️ Tiempo promedio de respuesta
   - 👥 Usuarios activos

3. Haz clic en **"Estadísticas Detalladas"** para ver:
   - Reportes por rango de fechas
   - Exportar datos (futuro)
   - Gráficas de tendencias

---

### Escenario 6: Solicitar Ayuda Psicológica

#### 📱 Como Repartidor

1. Login como `repartidor1`
2. Ve a **"Solicitar Ayuda"** en el menú
3. Llena el formulario:
   ```
   Nivel de urgencia: [1-10]
   Descripción: "He tenido varios incidentes esta semana y necesito apoyo"
   ```
4. Envía la solicitud

#### 👨‍💼 Verificación (Como Admin)

1. Login como `admin1`
2. Ve a **Django Admin** → http://localhost:8000/admin/
3. Busca **"Solicitudes de Ayuda Psicológica"**
4. Verás la solicitud registrada con:
   - Repartidor
   - Nivel de urgencia
   - Fecha
   - Estado: Pendiente

---

## 📱 Uso con Dispositivos Móviles

Para probar en tu teléfono real (recomendado para mejor experiencia):

### Opción 1: Usar ngrok (Recomendado)

1. **Instala ngrok** → https://ngrok.com/download

2. **Inicia tu servidor Django con Daphne**:
   ```bash
   # Terminal 1
   venv\Scripts\activate
   daphne -b 0.0.0.0 -p 8000 mysite.asgi:application
   ```

3. **Inicia ngrok** en otra terminal:
   ```bash
   # Terminal 2
   ngrok http 8000
   ```

4. **Copia la URL** que te da ngrok:
   ```
   Forwarding: https://abc123.ngrok-free.app → http://localhost:8000
   ```

5. **Configura Django** para aceptar el dominio:

   Edita `mysite/settings.py`:
   ```python
   ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'abc123.ngrok-free.app']

   CSRF_TRUSTED_ORIGINS = ['https://abc123.ngrok-free.app']
   ```

6. **Reinicia Daphne** y abre en tu móvil:
   ```
   https://abc123.ngrok-free.app
   ```

7. **Acepta permisos** en tu teléfono:
   - ✅ Ubicación/GPS
   - ✅ Notificaciones

8. **Prueba el botón de pánico** desde tu teléfono mientras monitorizas en tu computadora como operador

### Opción 2: Misma Red WiFi

1. **Obtén tu IP local** (Windows):
   ```bash
   ipconfig
   # Busca IPv4 Address: 192.168.X.X
   ```

2. **Configura Django**:
   ```python
   ALLOWED_HOSTS = ['localhost', '127.0.0.1', '192.168.X.X']
   ```

3. **Inicia servidor**:
   ```bash
   daphne -b 0.0.0.0 -p 8000 mysite.asgi:application
   ```

4. **Accede desde tu móvil**:
   ```
   http://192.168.X.X:8000
   ```

⚠️ **Nota**: Esta opción requiere HTTP, y algunos navegadores móviles pueden bloquear la API de Geolocalización en HTTP. Usa ngrok para HTTPS.

---

## 📂 Estructura del Proyecto

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

## 💾 Modelos de Base de Datos

| Modelo | Descripción | Campos Principales |
|--------|-------------|-------------------|
| 👤 **User** | Usuario extendido | Roles (repartidor/operador/admin), email único, teléfono |
| 📱 **RepartidorProfile** | Perfil del repartidor | Ubicación, batería, estado (disponible/emergencia/offline) |
| 🚨 **Alerta** | Emergencia activada | UUID, tipo (pánico/accidente), estado, ubicación, sensores |
| 📍 **Trayectoria** | Ruta durante alerta | Coordenadas, precisión, velocidad, timestamp |
| 📞 **ContactoConfianza** | Contactos (máx 3) | Nombre, teléfono, relación, validado |
| 📋 **Incidente** | Seguimiento operativo | Operador asignado, folio 911, tiempo de respuesta |
| 📝 **Bitacora** | Log de acciones | Descripción, operador, timestamp |
| 🗺️ **EstadisticaRiesgo** | Zonas peligrosas | Coordenadas, puntuación (0-100), conteo de alertas |
| 🧠 **SolicitudAyuda** | Apoyo psicológico | Urgencia (1-10), estado, confidencial |

> 📖 **Detalles técnicos completos**: Ver [FUNCIONAMIENTO.md](FUNCIONAMIENTO.md)

## ✨ Funcionalidades Implementadas

### ✅ Completadas (v1.0)
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

## 🎮 Guía Rápida de Uso

### 📱 Como Repartidor

1. **Login** → Dashboard con botón de pánico
2. **Mantén presionado** el botón rojo por 3 segundos
3. Tu ubicación se envía automáticamente cada 5 segundos
4. Gestiona hasta 3 **contactos de confianza**
5. Solicita **apoyo psicológico** cuando lo necesites

### 🖥️ Como Operador

1. **Login** → Dashboard de monitoreo en tiempo real
2. **Recibe alertas** instantáneas (< 5 segundos)
3. **Atiende emergencias** → Seguimiento con mapa en tiempo real
4. **Documenta acciones** en bitácora
5. **Cierra incidentes** cuando se resuelvan

### 👨‍💼 Como Administrador

1. **Login** → Dashboard con estadísticas
2. **Gestiona usuarios** (crear, editar, desactivar)
3. **Consulta reportes** por período y zona
4. **Django Admin** para acceso completo a la BD

> 💡 **Ver guía detallada**: Revisa la sección [Cómo Probar el Sistema](#-cómo-probar-el-sistema) para instrucciones paso a paso.

---

## 🔒 Seguridad

- Autenticación obligatoria para todas las rutas
- Verificación de roles para cada vista
- CSRF protection habilitado
- WebSockets con autenticación
- Sesiones de 24 horas con renovación automática
- Passwords hasheados con algoritmos seguros de Django

## 🛠️ Comandos Útiles

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

---

## 🔧 Solución de Problemas

### ❌ Error: "No module named 'channels'"

**Solución**:
```bash
pip install -r requirements.txt
```

### ❌ Error: "Geolocation no funciona"

**Causas posibles**:
1. **No aceptaste los permisos** → Revisa la barra de direcciones del navegador
2. **Estás usando HTTP** → Geolocation API requiere HTTPS (usa ngrok)
3. **Navegador no compatible** → Usa Chrome, Firefox o Safari modernos

### ❌ WebSockets no funcionan (operador no recibe alertas)

**Solución**:
1. Verifica que estés usando **Daphne**, no `runserver`:
   ```bash
   daphne -b 0.0.0.0 -p 8000 mysite.asgi:application
   ```

2. Abre la consola del navegador (F12) y busca errores de WebSocket

3. Verifica que no haya firewall bloqueando el puerto 8000

### ❌ Error: "CSRF token missing"

**Solución**:
1. Si usas ngrok, agrega el dominio a `CSRF_TRUSTED_ORIGINS` en `settings.py`
2. Asegúrate de que el formulario incluya `{% csrf_token %}`

### ❌ El mapa no se muestra

**Solución**:
1. Verifica tu conexión a internet (Leaflet.js se carga desde CDN)
2. Abre la consola (F12) y busca errores de JavaScript
3. Limpia el caché del navegador (Ctrl + Shift + R)

### ❌ Error: "Port 8000 already in use"

**Solución** (Windows):
```bash
# Ver qué proceso usa el puerto
netstat -ano | findstr :8000

# Matar el proceso (reemplaza <PID> con el número que aparece)
taskkill /PID <PID> /F
```

### ❌ CSS no se aplica (página sin estilos)

**Solución**:
```bash
# Compilar TailwindCSS
npm run build:css

# O en modo watch
npm run watch:css
```

### ❌ Error al crear migraciones

**Solución**:
```bash
# Eliminar migraciones conflictivas
# Luego volver a crear
python manage.py makemigrations
python manage.py migrate
```

### 💡 Tip: Ver logs en tiempo real

Para debug, abre la consola del navegador (F12) → pestaña "Console"

---

## 🚀 Deployment

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

---

## 📚 Documentación

### Documentos Disponibles

| Documento | Descripción | Para quién |
|-----------|-------------|------------|
| 📖 [FUNCIONAMIENTO.md](FUNCIONAMIENTO.md) | Documentación técnica detallada de la arquitectura, flujos de datos y componentes | Desarrolladores |
| 📝 README.md | Este archivo - Guía de inicio rápido | Todos |

### Contenido de FUNCIONAMIENTO.md

- **Arquitectura del Sistema**: Diagramas y explicación de ASGI, Channels, WebSockets
- **Flujo de Datos**: Cómo viajan los datos desde el repartidor hasta los operadores
- **Componentes**: Explicación profunda de modelos, consumers, views
- **Código Explicado**: Ejemplos con código de cómo funciona cada característica
- **Casos de Uso Técnicos**: Flujos completos con código paso a paso
- **Seguridad**: Cómo se implementa autenticación, autorización y validación
- **Escalabilidad**: Recomendaciones para producción

👉 **¿Quieres entender cómo funciona internamente el sistema?** Lee [FUNCIONAMIENTO.md](FUNCIONAMIENTO.md)

---

## 🤝 Soporte y Contacto

Para reportar problemas o solicitar nuevas funcionalidades, por favor crea un issue en el repositorio.

---

## 📄 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

---

## 💪 Contribuir

¿Quieres contribuir al proyecto?

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add: Amazing Feature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

Lee [FUNCIONAMIENTO.md](FUNCIONAMIENTO.md) para entender la arquitectura antes de contribuir.

---

## ⭐ Agradecimientos

- **Django** - Framework web robusto
- **Django Channels** - Soporte para WebSockets
- **TailwindCSS** - Framework CSS moderno
- **Leaflet.js** - Mapas interactivos
- Desarrollado con ☕ y mucho esfuerzo

---

<div align="center">

## 🚨 RappiSafe

**Sistema de Seguridad para Repartidores**

*Protegiendo a quienes nos entregan cada día*

[⬆ Volver arriba](#-rappisafe)

</div>
