# Cómo Funciona RappiSafe

## Índice
1. [Visión General](#visión-general)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Flujo de Datos](#flujo-de-datos)
4. [Componentes Principales](#componentes-principales)
5. [Funcionamiento de Características Clave](#funcionamiento-de-características-clave)
6. [Comunicación en Tiempo Real](#comunicación-en-tiempo-real)
7. [Seguridad y Autenticación](#seguridad-y-autenticación)
8. [Casos de Uso Detallados](#casos-de-uso-detallados)

---

## Visión General

RappiSafe es un sistema integral de seguridad para repartidores que combina geolocalización en tiempo real, comunicación bidireccional mediante WebSockets y un centro de monitoreo para atención de emergencias.

### Objetivo Principal
Proporcionar una respuesta rápida (< 5 segundos) ante situaciones de emergencia que enfrenten los repartidores durante su jornada laboral.

### Actores del Sistema
1. **Repartidor**: Usuario móvil que puede activar alertas de pánico
2. **Operador**: Personal del centro de monitoreo que atiende emergencias
3. **Administrador**: Gestiona usuarios, visualiza estadísticas y administra el sistema

---

## Arquitectura del Sistema

### Stack Tecnológico

```
┌─────────────────────────────────────────────────────────────┐
│                         FRONTEND                             │
│  Django Templates + TailwindCSS + Vanilla JavaScript        │
│  - Interfaz Responsive Mobile-First                          │
│  - Leaflet.js para mapas interactivos                        │
│  - Geolocation API para GPS                                  │
│  - WebSocket API para tiempo real                            │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│                    CAPA DE COMUNICACIÓN                      │
│              Django Channels + WebSockets                    │
│  - Comunicación bidireccional en tiempo real                │
│  - Grupos de canales para difusión selectiva                │
│  - Autenticación de conexiones WebSocket                    │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│                         BACKEND                              │
│                    Django 5.2.8                              │
│  - Lógica de negocio                                        │
│  - Sistema de autenticación y roles                         │
│  - APIs REST para operaciones CRUD                          │
│  - Signals para eventos automáticos                         │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│                    BASE DE DATOS                             │
│                      SQLite / PostgreSQL                     │
│  - Usuarios y perfiles                                      │
│  - Alertas y trayectorias                                   │
│  - Incidentes y bitácoras                                   │
│  - Estadísticas y zonas de riesgo                           │
└─────────────────────────────────────────────────────────────┘
```

### Arquitectura ASGI

El proyecto utiliza ASGI (Asynchronous Server Gateway Interface) en lugar de WSGI tradicional para soportar WebSockets:

```python
# mysite/asgi.py
application = ProtocolTypeRouter({
    "http": django_asgi_app,           # Peticiones HTTP normales
    "websocket": AuthMiddlewareStack(  # Conexiones WebSocket
        URLRouter(websocket_urlpatterns)
    ),
})
```

---

## Flujo de Datos

### 1. Flujo de Alerta de Pánico

```
┌──────────────┐
│  REPARTIDOR  │ Mantiene presionado botón por 3 segundos
└──────┬───────┘
       │ 1. Captura ubicación GPS
       │ 2. Captura nivel de batería
       │ 3. POST a /alertas/crear/
       ↓
┌──────────────┐
│   SERVIDOR   │ Crea alerta en BD con estado "pendiente"
└──────┬───────┘
       │ Signal post_save de Alerta
       │ Envía mensaje a grupo WebSocket "alertas"
       ↓
┌──────────────┐
│  OPERADORES  │ Reciben notificación instantánea
└──────┬───────┘     (todos los conectados al dashboard)
       │ Ven nueva alerta en dashboard
       │ Click en "Atender Alerta"
       ↓
┌──────────────┐
│   SERVIDOR   │ Actualiza estado a "en_atencion"
└──────┬───────┘ Crea Incidente asociado
       │ Envía actualización vía WebSocket
       ↓
┌──────────────┐
│  OPERADOR    │ Ve detalles completos del incidente
└──────────────┘ Inicia seguimiento en tiempo real
```

### 2. Flujo de Geolocalización en Tiempo Real

```
┌──────────────┐
│  REPARTIDOR  │ Alerta activa, intervalo cada 5 segundos
└──────┬───────┘
       │ navigator.geolocation.getCurrentPosition()
       │ WebSocket.send({ tipo: 'ubicacion', lat, lon, ... })
       ↓
┌──────────────┐
│  WebSocket   │ UbicacionConsumer.receive()
│   Consumer   │
└──────┬───────┘
       │ 1. Guarda en BD (Trayectoria)
       │ 2. Transmite a grupo "ubicacion_{alerta_id}"
       ↓
┌──────────────┐
│  OPERADOR    │ Recibe actualización
└──────────────┘ Actualiza marcador en mapa
                 Actualiza línea de trayectoria
```

### 3. Flujo de Autenticación y Roles

```
┌──────────────┐
│   USUARIO    │ Ingresa username/password
└──────┬───────┘
       │ POST a /accounts/login/
       ↓
┌──────────────┐
│   DJANGO     │ Valida credenciales
│   AUTH       │ Crea sesión
└──────┬───────┘
       │ Verifica campo "rol" del usuario
       ↓
     ┌─┴─────────────────┐
     │  Redirección       │
     ├───────────────────┤
     │ repartidor    → /repartidor/dashboard/
     │ operador      → /operador/dashboard/
     │ administrador → /admin/dashboard/
     └────────────────────┘
```

---

## Componentes Principales

### 1. Modelos de Datos

#### User (Usuario Extendido)
```python
class User(AbstractUser):
    rol = ['repartidor', 'operador', 'administrador']
    email = EmailField(unique=True)
    telefono = CharField(validado con regex)
    activo = BooleanField()
```

**Función**: Gestiona autenticación y autorización basada en roles.

#### RepartidorProfile
```python
class RepartidorProfile:
    user = OneToOneField(User)
    ultima_latitud, ultima_longitud
    nivel_bateria
    estado = ['disponible', 'en_ruta', 'emergencia', 'offline']
    sensibilidad_agitacion
```

**Función**: Almacena información extendida del repartidor y su estado en tiempo real.

#### Alerta
```python
class Alerta:
    id = UUIDField()  # Identificador único
    repartidor = ForeignKey(User)
    tipo = ['panico', 'accidente']
    estado = ['pendiente', 'en_atencion', 'atendida', 'cerrada', 'falsa_alarma']
    latitud, longitud
    nivel_bateria
    datos_sensores = JSONField()
```

**Función**: Representa cada emergencia activada por un repartidor.

#### Trayectoria
```python
class Trayectoria:
    alerta = ForeignKey(Alerta)
    latitud, longitud
    precision  # Precisión del GPS en metros
    velocidad  # Velocidad del dispositivo
    timestamp
```

**Función**: Almacena cada punto de la ruta del repartidor durante una alerta.

#### Incidente
```python
class Incidente:
    alerta = OneToOneField(Alerta)
    operador = ForeignKey(User)
    folio_911
    descripcion
    acciones_tomadas
    tiempo_respuesta
```

**Función**: Documenta el seguimiento operativo de cada emergencia.

#### ContactoConfianza
```python
class ContactoConfianza:
    repartidor = ForeignKey(User)
    nombre, telefono, relacion
    validado = BooleanField()
```

**Función**: Almacena hasta 3 contactos que son notificados en emergencias.

### 2. WebSocket Consumers

#### AlertasConsumer
```python
class AlertasConsumer(AsyncWebsocketConsumer):
    group_name = 'alertas'
```

**Función**:
- Conecta a operadores al grupo de alertas
- Transmite nuevas alertas a todos los operadores en tiempo real
- Transmite actualizaciones de estado de alertas

**Flujo**:
```
1. Operador abre dashboard → connect()
2. Se une al grupo "alertas" → group_add()
3. Cuando se crea/actualiza alerta → group_send()
4. Todos los operadores reciben → nueva_alerta() / actualizar_alerta()
```

#### UbicacionConsumer
```python
class UbicacionConsumer(AsyncWebsocketConsumer):
    group_name = f'ubicacion_{alerta_id}'
```

**Función**:
- Recibe actualizaciones de ubicación del repartidor
- Guarda cada punto en la base de datos (Trayectoria)
- Transmite ubicación a operadores monitoreando esa alerta

**Flujo**:
```
1. Repartidor/Operador se conecta → connect()
2. Se une a grupo específico de la alerta → group_add()
3. Repartidor envía ubicación → receive()
4. Guarda en BD → guardar_trayectoria()
5. Transmite a grupo → actualizar_ubicacion()
```

#### MonitoreoConsumer
```python
class MonitoreoConsumer(AsyncWebsocketConsumer):
    group_name = 'monitoreo_general'
```

**Función**:
- Proporciona vista general del sistema
- Transmite estadísticas en tiempo real
- Notifica cambios de estado de repartidores

### 3. Views Principales

#### Repartidor
- `repartidor_dashboard`: Vista principal con botón de pánico
- `crear_alerta`: POST para crear nueva alerta
- `cancelar_alerta`: Cancela alerta activa
- `alertas_activas`: Lista alertas del repartidor
- `gestionar_contactos`: CRUD de contactos de confianza

#### Operador
- `operador_dashboard`: Dashboard con WebSocket de alertas
- `monitoreo_alerta`: Vista de seguimiento individual con mapa
- `atender_alerta`: Toma responsabilidad de una alerta
- `actualizar_incidente`: Agrega acciones a la bitácora
- `cerrar_incidente`: Cierra y documenta la resolución

#### Administrador
- `admin_dashboard`: Estadísticas y métricas
- `gestionar_usuarios`: CRUD de usuarios
- `estadisticas_periodo`: Reportes por fechas
- `zonas_riesgo`: Mapa de calor de incidentes

---

## Funcionamiento de Características Clave

### 1. Botón de Pánico

**Implementación Frontend** (`repartidor/dashboard.html`):
```javascript
let holdTimer;
let progressInterval;

panicButton.addEventListener('mousedown', () => {
    startTime = Date.now();
    progressBar.style.width = '0%';

    // Actualiza barra de progreso cada 50ms
    progressInterval = setInterval(() => {
        let progress = ((Date.now() - startTime) / 3000) * 100;
        progressBar.style.width = progress + '%';
    }, 50);

    // Activa alerta después de 3 segundos
    holdTimer = setTimeout(() => {
        activarAlerta();
    }, 3000);
});

panicButton.addEventListener('mouseup', () => {
    clearTimeout(holdTimer);
    clearInterval(progressInterval);
    progressBar.style.width = '0%';
});
```

**Por qué 3 segundos**: Previene activaciones accidentales mientras permite respuesta rápida en emergencias reales.

### 2. Geolocalización en Tiempo Real

**Captura de Ubicación**:
```javascript
function obtenerUbicacion() {
    if (!navigator.geolocation) {
        alert('Tu navegador no soporta geolocalización');
        return;
    }

    navigator.geolocation.getCurrentPosition(
        (position) => {
            const datos = {
                tipo: 'ubicacion',
                latitud: position.coords.latitude,
                longitud: position.coords.longitude,
                precision: position.coords.accuracy,
                velocidad: position.coords.speed,
                timestamp: new Date().toISOString()
            };

            // Enviar por WebSocket
            ubicacionSocket.send(JSON.stringify(datos));
        },
        (error) => {
            console.error('Error GPS:', error);
        },
        {
            enableHighAccuracy: true,  // Máxima precisión
            timeout: 5000,
            maximumAge: 0  // No usar ubicación en caché
        }
    );
}

// Intervalo cada 5 segundos durante alerta activa
let ubicacionInterval = setInterval(obtenerUbicacion, 5000);
```

**Visualización en Mapa** (Operador):
```javascript
// Mapa Leaflet
const mapa = L.map('mapa').setView([lat, lon], 15);
let marcador = L.marker([lat, lon]).addTo(mapa);
let trayectoria = L.polyline([], {color: 'red'}).addTo(mapa);

// Al recibir actualización
ubicacionSocket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.tipo === 'ubicacion') {
        // Actualizar marcador
        marcador.setLatLng([data.latitud, data.longitud]);

        // Agregar punto a trayectoria
        trayectoria.addLatLng([data.latitud, data.longitud]);

        // Centrar mapa
        mapa.panTo([data.latitud, data.longitud]);
    }
};
```

### 3. Sistema de WebSockets

**Conexión en Cliente**:
```javascript
// Conectar a canal de alertas (Operador)
const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const alertasSocket = new WebSocket(
    `${protocol}//${window.location.host}/ws/alertas/`
);

alertasSocket.onopen = () => {
    console.log('Conectado al canal de alertas');
};

alertasSocket.onmessage = (event) => {
    const data = JSON.parse(event.data);

    if (data.tipo === 'nueva_alerta') {
        mostrarNotificacion(data.alerta);
        reproducirSonido();
        actualizarListaAlertas(data.alerta);
    }

    if (data.tipo === 'actualizar_alerta') {
        actualizarEstadoAlerta(data.alerta);
    }
};

alertasSocket.onerror = (error) => {
    console.error('Error WebSocket:', error);
};

alertasSocket.onclose = () => {
    console.log('Desconectado. Intentando reconectar...');
    setTimeout(() => {
        location.reload();  // Reconexión simple
    }, 3000);
};
```

**Envío desde Backend** (Signal):
```python
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

@receiver(post_save, sender=Alerta)
def notificar_nueva_alerta(sender, instance, created, **kwargs):
    if created:  # Solo para alertas nuevas
        channel_layer = get_channel_layer()

        # Serializar datos de la alerta
        alerta_data = {
            'id': str(instance.id),
            'repartidor': instance.repartidor.get_full_name(),
            'tipo': instance.get_tipo_display(),
            'latitud': float(instance.latitud),
            'longitud': float(instance.longitud),
            'nivel_bateria': instance.nivel_bateria,
            'creado_en': instance.creado_en.isoformat(),
        }

        # Enviar a grupo de alertas
        async_to_sync(channel_layer.group_send)(
            'alertas',
            {
                'type': 'nueva_alerta',
                'alerta': alerta_data
            }
        )
```

### 4. Notificaciones del Navegador

```javascript
// Solicitar permiso al cargar página
if ('Notification' in window) {
    Notification.requestPermission();
}

// Mostrar notificación
function mostrarNotificacion(alerta) {
    if (Notification.permission === 'granted') {
        const notificacion = new Notification('🚨 Nueva Alerta de Emergencia', {
            body: `${alerta.repartidor} activó botón de pánico`,
            icon: '/static/img/logo.png',
            badge: '/static/img/badge.png',
            vibrate: [200, 100, 200],
            tag: alerta.id,  // Evita duplicados
            requireInteraction: true  // No desaparece automáticamente
        });

        notificacion.onclick = () => {
            window.focus();
            window.location.href = `/operador/monitoreo/${alerta.id}/`;
        };
    }
}
```

### 5. Monitoreo de Batería

```javascript
// Battery API
if ('getBattery' in navigator) {
    navigator.getBattery().then((battery) => {
        function actualizarBateria() {
            const nivel = Math.round(battery.level * 100);

            // Actualizar UI
            document.getElementById('bateria').textContent = nivel + '%';

            // Enviar a servidor si cambió significativamente
            if (Math.abs(nivel - nivelAnterior) >= 5) {
                fetch('/api/actualizar-bateria/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify({ nivel: nivel })
                });
                nivelAnterior = nivel;
            }
        }

        // Actualizar cada 60 segundos
        actualizarBateria();
        setInterval(actualizarBateria, 60000);

        // Listeners de cambios
        battery.addEventListener('levelchange', actualizarBateria);
        battery.addEventListener('chargingchange', actualizarBateria);
    });
}
```

---

## Comunicación en Tiempo Real

### Arquitectura de Channels

```
┌─────────────────────────────────────────────────────────────┐
│                    Channel Layer                             │
│              (In-Memory / Redis)                             │
│                                                              │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐                │
│  │  Grupo:  │   │  Grupo:  │   │  Grupo:  │                │
│  │ alertas  │   │ubicacion │   │monitoreo │                │
│  │          │   │ _123-abc │   │ _general │                │
│  ├──────────┤   ├──────────┤   ├──────────┤                │
│  │ channel1 │   │ channel3 │   │ channel5 │                │
│  │ channel2 │   │ channel4 │   │ channel6 │                │
│  │ channel7 │   │          │   │          │                │
│  └──────────┘   └──────────┘   └──────────┘                │
└─────────────────────────────────────────────────────────────┘
        ↕               ↕               ↕
┌──────────┐    ┌──────────┐    ┌──────────┐
│Operador 1│    │Operador 2│    │Repartidor│
│ Browser  │    │ Browser  │    │  Mobile  │
└──────────┘    └──────────┘    └──────────┘
```

### Grupos de Canales

1. **Grupo "alertas"**:
   - Todos los operadores conectados
   - Reciben notificaciones de nuevas alertas
   - Reciben actualizaciones de estado

2. **Grupo "ubicacion_{alerta_id}"**:
   - Repartidor con alerta activa
   - Operador monitoreando esa alerta
   - Actualizaciones de ubicación cada 5s

3. **Grupo "monitoreo_general"**:
   - Dashboard administrativo
   - Estadísticas en tiempo real
   - Estados de todos los repartidores

### Ventajas de WebSockets sobre Polling

**Polling tradicional** (consultar cada X segundos):
```
Cliente → Servidor: ¿Hay alertas nuevas?
Servidor → Cliente: No
[Espera 3 segundos]
Cliente → Servidor: ¿Hay alertas nuevas?
Servidor → Cliente: No
[Espera 3 segundos]
Cliente → Servidor: ¿Hay alertas nuevas?
Servidor → Cliente: Sí, aquí está
```
**Problemas**: Latencia, sobrecarga del servidor, uso de bandwidth

**WebSockets** (conexión persistente):
```
Cliente ←→ Servidor: [Conexión establecida]
[Silencio hasta que hay datos]
Servidor → Cliente: Nueva alerta inmediatamente
```
**Ventajas**:
- Latencia < 1 segundo
- Menos carga en servidor
- Bidireccional
- Eficiente en bandwidth

---

## Seguridad y Autenticación

### 1. Autenticación de WebSockets

```python
class AlertasConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Verificar autenticación
        if self.scope["user"] == AnonymousUser():
            await self.close()
            return

        # Verificar rol
        user = self.scope["user"]
        if user.rol not in ['operador', 'administrador']:
            await self.close()
            return

        # Conexión autorizada
        await self.accept()
```

### 2. Middleware de Autenticación

Django Channels utiliza `AuthMiddlewareStack` para pasar la sesión del usuario a las conexiones WebSocket:

```python
# mysite/asgi.py
websocket = AuthMiddlewareStack(
    URLRouter(websocket_urlpatterns)
)
```

Esto permite que `self.scope["user"]` contenga el usuario autenticado de Django.

### 3. Protección CSRF

```javascript
// Obtener token CSRF
const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

// Incluir en todas las peticiones POST
fetch(url, {
    method: 'POST',
    headers: {
        'X-CSRFToken': csrfToken,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
});
```

### 4. Validación de Roles

**Decorador personalizado**:
```python
from functools import wraps
from django.shortcuts import redirect

def rol_requerido(*roles_permitidos):
    def decorador(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')

            if request.user.rol not in roles_permitidos:
                return redirect('sin_permiso')

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorador

# Uso
@rol_requerido('operador', 'administrador')
def operador_dashboard(request):
    # Solo accesible para operadores y admins
    pass
```

### 5. Validación de Datos

```python
# En views
def crear_alerta(request):
    if request.method == 'POST':
        try:
            # Validar campos requeridos
            latitud = Decimal(request.POST.get('latitud'))
            longitud = Decimal(request.POST.get('longitud'))

            # Validar rangos
            if not (-90 <= latitud <= 90):
                return JsonResponse({'error': 'Latitud inválida'}, status=400)
            if not (-180 <= longitud <= 180):
                return JsonResponse({'error': 'Longitud inválida'}, status=400)

            # Crear alerta
            alerta = Alerta.objects.create(
                repartidor=request.user,
                tipo='panico',
                latitud=latitud,
                longitud=longitud,
                # ...
            )

            return JsonResponse({'id': str(alerta.id)})

        except (ValueError, InvalidOperation):
            return JsonResponse({'error': 'Datos inválidos'}, status=400)
```

---

## Casos de Uso Detallados

### Caso 1: Activación de Alerta de Pánico

**Actores**: Repartidor, Sistema, Operadores

**Precondiciones**:
- Repartidor autenticado
- GPS habilitado
- Sin alertas activas previas

**Flujo**:

1. **Repartidor** mantiene presionado el botón de pánico durante 3 segundos
   - Frontend muestra barra de progreso visual
   - Si suelta antes de 3s, se cancela

2. **Frontend** captura datos del dispositivo:
   ```javascript
   {
       latitud: 19.432608,
       longitud: -99.133209,
       precision: 10.5,  // metros
       nivel_bateria: 67,
       timestamp: "2024-01-20T15:30:45.123Z"
   }
   ```

3. **Frontend** envía POST a `/alertas/crear/`:
   - Incluye token CSRF
   - Incluye todos los datos capturados

4. **Backend** procesa la petición:
   ```python
   alerta = Alerta.objects.create(
       id=uuid.uuid4(),
       repartidor=request.user,
       tipo='panico',
       estado='pendiente',
       latitud=latitud,
       longitud=longitud,
       nivel_bateria=nivel_bateria
   )
   ```

5. **Signal** `post_save` se dispara automáticamente:
   - Serializa datos de la alerta
   - Envía a grupo WebSocket "alertas"
   - Actualiza estado del repartidor a "emergencia"

6. **Todos los operadores conectados** reciben la alerta:
   - WebSocket entrega mensaje en < 1 segundo
   - Aparece notificación sonora
   - Aparece notificación del navegador
   - Se agrega a lista de alertas pendientes

7. **Frontend del repartidor**:
   - Muestra confirmación visual
   - Abre conexión WebSocket de ubicación
   - Inicia envío de ubicación cada 5 segundos
   - Muestra opción de cancelar

8. **Operador** ve la alerta y puede:
   - Ver ubicación en el mapa
   - Ver información del repartidor
   - Hacer clic en "Atender Alerta"

**Postcondiciones**:
- Alerta creada en BD con estado "pendiente"
- Todos los operadores notificados
- Repartidor enviando ubicación activamente
- Sistema registrando trayectoria

**Tiempos**:
- Activación del botón: 3 segundos
- Creación en BD: < 100ms
- Notificación a operadores: < 1 segundo
- **Total: < 5 segundos** ✅

### Caso 2: Atención de Emergencia por Operador

**Actores**: Operador, Sistema, Repartidor

**Precondiciones**:
- Alerta en estado "pendiente"
- Operador autenticado
- Operador en dashboard

**Flujo**:

1. **Operador** ve alerta en dashboard:
   ```
   🚨 Juan Pérez - Pánico
   📍 Av. Insurgentes Sur 1234, CDMX
   🔋 67% batería
   ⏰ Hace 30 segundos
   ```

2. **Operador** hace clic en "Atender Alerta":
   - POST a `/operador/atender/<alerta_id>/`
   - Sistema valida que no esté ya atendida

3. **Backend** actualiza estados:
   ```python
   with transaction.atomic():
       alerta.estado = 'en_atencion'
       alerta.save()

       incidente = Incidente.objects.create(
           alerta=alerta,
           operador=request.user,
           estado='en_curso',
           inicio_atencion=timezone.now()
       )

       Bitacora.objects.create(
           incidente=incidente,
           operador=request.user,
           tipo='inicio_atencion',
           descripcion=f'Alerta atendida por {request.user.get_full_name()}'
       )
   ```

4. **Sistema** notifica cambio:
   - WebSocket envía actualización a grupo "alertas"
   - Otros operadores ven que ya está siendo atendida
   - Repartidor recibe confirmación (opcional)

5. **Operador** es redirigido a vista de monitoreo:
   - `/operador/monitoreo/<alerta_id>/`
   - Mapa con ubicación en tiempo real
   - Panel con información del repartidor
   - Lista de contactos de confianza
   - Formulario de bitácora

6. **Operador** ve trayectoria en tiempo real:
   - WebSocket "ubicacion_{alerta_id}" conectado
   - Marcador actualizado cada 5 segundos
   - Línea roja muestra recorrido

7. **Operador** toma acciones:

   a) **Llamar al repartidor**:
   ```
   Teléfono: +52 55 1234 5678
   [Botón: Llamar]
   ```

   b) **Contactar a confianza**:
   ```
   Contacto 1: María Pérez (Esposa)
   +52 55 8765 4321
   [Botón: Llamar]
   ```

   c) **Llamar al 911**:
   - Ingresa folio del reporte
   - Registra en bitácora

8. **Operador** documenta acciones:
   ```
   15:31 - Alerta recibida y atendida
   15:32 - Llamada a repartidor, no contesta
   15:33 - Llamada a contacto de confianza (esposa)
   15:35 - Contacto confirma ubicación, va en camino
   15:40 - Llamada al 911, folio: 123456789
   15:45 - Patrulla llegó al lugar
   15:50 - Repartidor confirma que está bien, falsa alarma
   ```

9. **Operador** cierra el incidente:
   - Selecciona resultado: "Falsa Alarma" / "Atendida" / "Cerrada"
   - Ingresa descripción final
   - POST a `/operador/cerrar/<incidente_id>/`

10. **Sistema** finaliza:
    ```python
    with transaction.atomic():
        alerta.estado = 'falsa_alarma'  # o 'cerrada'
        alerta.save()

        incidente.estado = 'cerrado'
        incidente.fin_atencion = timezone.now()
        incidente.tiempo_respuesta = (
            incidente.fin_atencion - incidente.inicio_atencion
        ).total_seconds()
        incidente.save()

        perfil.estado = 'disponible'
        perfil.save()
    ```

**Postcondiciones**:
- Incidente documentado completamente
- Tiempos de respuesta registrados
- Estadísticas actualizadas
- Repartidor vuelve a estado normal

### Caso 3: Gestión de Contactos de Confianza

**Actores**: Repartidor, Sistema

**Precondiciones**:
- Repartidor autenticado
- Máximo 3 contactos configurados

**Flujo**:

1. **Repartidor** accede a "Mis Contactos de Confianza"
   - GET a `/repartidor/contactos/`
   - Ve lista actual (0-3 contactos)

2. **Repartidor** agrega nuevo contacto:
   ```
   Nombre: María Pérez
   Teléfono: +52 55 8765 4321
   Relación: Esposa
   ```

3. **Frontend** valida:
   - Campos no vacíos
   - Formato de teléfono correcto
   - No excede límite de 3

4. **Backend** crea contacto:
   ```python
   if repartidor.contactos.count() >= 3:
       return JsonResponse({
           'error': 'Máximo 3 contactos permitidos'
       }, status=400)

   contacto = ContactoConfianza.objects.create(
       repartidor=request.user,
       nombre=nombre,
       telefono=telefono,
       relacion=relacion,
       validado=False  # Requiere validación posterior
   )
   ```

5. **Sistema** puede enviar SMS de validación (futuro):
   - Código de 6 dígitos
   - Contacto confirma para activar
   - `contacto.validado = True`

**Postcondiciones**:
- Contacto guardado en BD
- Disponible para operadores en emergencias
- Visible en perfil del repartidor

---

## Métricas y Rendimiento

### Objetivos de Rendimiento

- **Tiempo de notificación**: < 5 segundos desde activación hasta operador
- **Actualización de ubicación**: Cada 5 segundos durante alerta
- **Precisión GPS**: < 20 metros en condiciones óptimas
- **Tiempo de respuesta del servidor**: < 200ms por petición
- **Disponibilidad**: 99.9% uptime

### Monitoreo

El sistema registra automáticamente:
- Tiempo de respuesta de cada incidente
- Cantidad de alertas por hora/día/mes
- Zonas geográficas con más incidentes
- Nivel de batería promedio al momento de alertas
- Tasa de falsas alarmas

Estos datos se visualizan en el dashboard administrativo.

---

## Escalabilidad

### Para Producción

**Cambios recomendados**:

1. **Base de Datos**: SQLite → PostgreSQL
   - Mejor rendimiento para escrituras concurrentes
   - Soporte para queries geoespaciales (PostGIS)

2. **Channel Layer**: In-Memory → Redis
   ```python
   CHANNEL_LAYERS = {
       'default': {
           'BACKEND': 'channels_redis.core.RedisChannelLayer',
           'CONFIG': {
               "hosts": [('redis-server', 6379)],
           },
       },
   }
   ```
   - Permite múltiples instancias de Daphne
   - Persiste mensajes entre reinicios

3. **Servidor Web**: Nginx + Daphne
   ```
   [Internet] → [Nginx:443] → [Daphne:8000] → [Django App]
                      ↓
               [Static Files]
   ```

4. **HTTPS Obligatorio**:
   - Geolocation API requiere HTTPS
   - WebSockets seguros (WSS)
   - Let's Encrypt para certificados

5. **Notificaciones SMS**: Integración con Twilio/Nexmo
   - Enviar SMS a contactos de confianza
   - Confirmación de incidentes cerrados

---

## Conclusión

RappiSafe es un sistema robusto que combina tecnologías web modernas para proporcionar una solución de seguridad en tiempo real. La arquitectura basada en Django Channels y WebSockets permite comunicación instantánea, mientras que el diseño mobile-first y la integración con APIs del navegador proporcionan una experiencia de usuario fluida.

El sistema está diseñado para escalar y puede adaptarse fácilmente a diferentes contextos más allá de la entrega de comida, como mensajería, transporte público, o cualquier servicio que requiera monitoreo de seguridad en tiempo real.

---

**Documentación actualizada**: Enero 2024
**Versión del sistema**: 1.0
**Mantenedor**: RappiSafe Team
