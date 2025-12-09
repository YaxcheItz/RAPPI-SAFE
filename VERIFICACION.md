# Lista de Verificación - Rappi Safe

Este documento te ayudará a verificar que todos los componentes del sistema funcionen correctamente.

## Pre-requisitos

Antes de iniciar, verifica que tienes instalado:

- [ ] Python 3.10 o superior
  ```bash
  python --version
  ```

- [ ] pip actualizado
  ```bash
  pip --version
  ```

- [ ] Node.js 18 o superior
  ```bash
  node --version
  ```

- [ ] npm
  ```bash
  npm --version
  ```

## Instalación

### 1. Dependencias Python

```bash
pip install -r requirements.txt
```

**Verificar**: No debe haber errores. Si hay problemas con alguna librería, intenta instalarla individualmente.

### 2. Dependencias Node.js

```bash
npm install
```

**Verificar**: Se debe crear la carpeta `node_modules/` con TailwindCSS.

### 3. Compilar CSS

```bash
npm run build:css
```

**Verificar**: Se debe crear/actualizar el archivo `static/css/output.css` y debe tener contenido (no estar vacío).

### 4. Migraciones de Base de Datos

```bash
python manage.py makemigrations
python manage.py migrate
```

**Verificar**:
- Se debe crear el archivo `db.sqlite3`
- No debe haber errores
- Debe mostrar las migraciones aplicadas

### 5. Datos de Prueba

```bash
python manage.py init_demo_data
```

**Verificar**:
- Debe mostrar "✓" en verde para cada elemento creado
- Si muestra "⚠" significa que ya existe (está bien)
- Al final debe mostrar la lista de usuarios creados

## Verificación de Componentes

### Backend

#### 1. Servidor Django

```bash
python manage.py runserver
```

**Verificar**:
- El servidor inicia sin errores
- Muestra la URL: http://127.0.0.1:8000/
- No hay errores en rojo

#### 2. Servidor con WebSockets (Daphne)

```bash
daphne -b 0.0.0.0 -p 8000 mysite.asgi:application
```

**Verificar**:
- El servidor inicia con Daphne
- Muestra "Listening on TCP address 0.0.0.0:8000"

#### 3. Django Admin

1. Accede a: http://localhost:8000/admin/
2. Login con: `admin` / `admin123`

**Verificar**:
- [x] La página de admin carga correctamente
- [x] Puedes ver los modelos de rappiSafe
- [x] Puedes ver usuarios, alertas, etc.

### Frontend

#### 1. Página de Login

1. Accede a: http://localhost:8000/
2. Verifica:
   - [x] El diseño es atractivo (fondo rojo, formulario centrado)
   - [x] Los estilos de TailwindCSS se aplican correctamente
   - [x] No hay errores en la consola del navegador (F12)

#### 2. Login como Repartidor

1. Usuario: `repartidor1`
2. Contraseña: `test123`
3. Click en "Iniciar Sesión"

**Verificar**:
- [x] Redirige al dashboard del repartidor
- [x] Se muestra el botón de pánico (círculo rojo grande)
- [x] El navbar muestra el nombre del usuario
- [x] El rol se muestra como "Repartidor"

#### 3. Botón de Pánico

1. En el dashboard del repartidor
2. Mantén presionado el botón rojo 3 segundos
3. Acepta los permisos de ubicación

**Verificar**:
- [x] Aparece un círculo de progreso
- [x] El mensaje cambia a "Manteniendo..."
- [x] Después de 3 segundos se activa
- [x] Muestra "¡Alerta activada!"
- [x] La página se recarga mostrando la alerta activa
- [x] Si sueltas antes de 3 segundos, muestra "Presión muy corta"

#### 4. Contactos de Confianza

1. Click en "Contactos" desde el dashboard
2. Click en "Agregar Contacto"
3. Llena el formulario:
   - Nombre: "Pedro González"
   - Teléfono: "+5215512345678"
   - Relación: "Hermano"
4. Click en "Guardar"

**Verificar**:
- [x] El modal se cierra
- [x] La página se recarga
- [x] El contacto aparece en la lista
- [x] Muestra el badge "Pendiente"

#### 5. Ayuda Psicológica

1. Click en "Ayuda Psicológica" desde el dashboard
2. Escribe una descripción
3. Ajusta el nivel de urgencia
4. Click en "Enviar Solicitud"

**Verificar**:
- [x] Muestra mensaje de confirmación
- [x] Redirige al home
- [x] La solicitud se guarda (verifica en Django Admin)

### Dashboard de Operadores

#### 1. Login como Operador

1. Logout del repartidor
2. Login con: `operador1` / `test123`

**Verificar**:
- [x] Redirige al dashboard de monitoreo
- [x] Se muestra el mapa (Leaflet.js)
- [x] Se muestra la lista de alertas activas (si hay alguna)
- [x] El indicador de WebSocket muestra "Conectando..." luego "Conectado" (punto verde)

#### 2. Ver Alerta (si hay alertas activas)

1. Click en una alerta de la lista
2. Verifica la página de detalle

**Verificar**:
- [x] Se muestra la información del repartidor
- [x] Se muestra el mapa con la ubicación
- [x] Se muestran los contactos de confianza
- [x] Hay botones para atender/cerrar
- [x] Se puede agregar a bitácora

#### 3. Atender Alerta

1. En la página de detalle de una alerta
2. Click en "Atender Alerta"

**Verificar**:
- [x] El estado cambia a "En Atención"
- [x] Se crea un incidente automáticamente
- [x] Aparece la sección de bitácora
- [x] Se puede registrar folio 911

#### 4. Cerrar Alerta

1. Click en "Cerrar Alerta"
2. Ingresa notas (opcional)
3. Confirma

**Verificar**:
- [x] La alerta se marca como cerrada
- [x] Redirige al dashboard
- [x] La alerta ya no aparece en alertas activas

### WebSockets en Tiempo Real

#### 1. Preparación

1. Asegúrate de ejecutar con Daphne:
   ```bash
   daphne -b 0.0.0.0 -p 8000 mysite.asgi:application
   ```

2. Abre dos navegadores (o dos ventanas de incógnito):
   - Navegador A: Login como `repartidor1`
   - Navegador B: Login como `operador1`

#### 2. Prueba de Tiempo Real

1. En Navegador B (operador), ve al dashboard de monitoreo
2. Verifica que el indicador WebSocket esté verde
3. En Navegador A (repartidor), activa el botón de pánico
4. Observa el Navegador B

**Verificar**:
- [x] En menos de 5 segundos aparece la nueva alerta en el dashboard del operador
- [x] Suena una alerta (si los permisos están activados)
- [x] Aparece notificación del navegador
- [x] La alerta aparece en el mapa
- [x] La alerta aparece en la lista lateral

### Dashboard de Administrador

#### 1. Login como Administrador

1. Logout
2. Login con: `admin1` / `test123`

**Verificar**:
- [x] Redirige al dashboard del administrador
- [x] Se muestran estadísticas (total usuarios, repartidores, operadores, alertas)
- [x] Hay tarjetas con accesos rápidos

#### 2. Gestión de Usuarios

1. Click en "Gestionar Usuarios"
2. Prueba los filtros (por rol, por estado)
3. Click en "Editar" en algún usuario

**Verificar**:
- [x] La lista se muestra correctamente
- [x] Los filtros funcionan
- [x] El botón "Editar" lleva al Django Admin
- [x] La paginación funciona (si hay más de 20 usuarios)

#### 3. Estadísticas

1. Click en "Estadísticas"
2. Prueba cambiar las fechas
3. Click en "Consultar"

**Verificar**:
- [x] Se muestran las estadísticas
- [x] Hay tarjetas con totales
- [x] Se muestran las zonas de riesgo
- [x] Los filtros de fecha funcionan

## Verificación de Consola del Navegador

Abre las herramientas de desarrollador (F12) y verifica:

### Console (Consola)

- [ ] No hay errores en rojo
- [ ] Los mensajes de WebSocket se ven (si estás en dashboard de operador)
- [ ] No hay warnings críticos

### Network (Red)

- [ ] Las peticiones a `/ws/` (WebSocket) tienen status "101 Switching Protocols"
- [ ] Las peticiones AJAX retornan 200 OK
- [ ] Los archivos CSS y JS se cargan correctamente

### Application (Aplicación)

- [ ] Las cookies de sesión están configuradas
- [ ] El localStorage tiene data si se usa

## Verificación de Base de Datos

```bash
python manage.py shell
```

```python
from rappiSafe.models import *

# Verificar usuarios
print(f"Total usuarios: {User.objects.count()}")
print(f"Repartidores: {User.objects.filter(rol='repartidor').count()}")
print(f"Operadores: {User.objects.filter(rol='operador').count()}")

# Verificar alertas
print(f"Total alertas: {Alerta.objects.count()}")
print(f"Alertas activas: {Alerta.objects.filter(estado__in=['pendiente','en_atencion']).count()}")

# Verificar perfiles de repartidores
print(f"Perfiles: {RepartidorProfile.objects.count()}")

# Verificar contactos
print(f"Contactos de confianza: {ContactoConfianza.objects.count()}")

# Salir
exit()
```

**Verificar**: Todos los contadores deben mostrar números mayores a 0.

## Problemas Comunes y Soluciones

### 1. CSS no se aplica

**Solución:**
```bash
npm run build:css
```
Luego recarga con Ctrl+F5

### 2. WebSockets no funcionan

**Causa**: Estás usando `python manage.py runserver`

**Solución**: Usa Daphne:
```bash
daphne -b 0.0.0.0 -p 8000 mysite.asgi:application
```

### 3. Error al crear alertas

**Causa**: Permisos de geolocalización no concedidos

**Solución**:
- Chrome: Click en el candado en la barra de direcciones
- Permitir ubicación
- Recarga la página

### 4. No se ven los modelos en Django Admin

**Causa**: No has hecho las migraciones

**Solución**:
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Import error con channels

**Causa**: No has instalado las dependencias

**Solución**:
```bash
pip install -r requirements.txt
```

## Lista de Verificación Final

Marca todos los items que funcionan correctamente:

### Backend
- [ ] Django servidor inicia sin errores
- [ ] Daphne servidor inicia sin errores
- [ ] Base de datos creada correctamente
- [ ] Migraciones aplicadas
- [ ] Datos de prueba creados
- [ ] Django Admin funciona

### Frontend
- [ ] Login carga con estilos correctos
- [ ] Dashboard repartidor funciona
- [ ] Botón de pánico funciona (3 segundos)
- [ ] Contactos de confianza funciona
- [ ] Ayuda psicológica funciona
- [ ] Dashboard operador carga con mapa
- [ ] Ver detalle de alerta funciona
- [ ] Dashboard admin funciona
- [ ] Gestión de usuarios funciona
- [ ] Estadísticas funcionan

### Tiempo Real
- [ ] WebSockets conectan correctamente
- [ ] Alertas aparecen en tiempo real
- [ ] Notificaciones suenan
- [ ] Notificaciones del navegador aparecen
- [ ] Actualización de ubicación funciona

### Navegadores Probados
- [ ] Chrome/Edge
- [ ] Firefox
- [ ] Safari (si está disponible)
- [ ] Móvil (Android/iOS vía navegador)

## Resultado

Si todos los items están marcados: ✅ **El sistema está completamente funcional**

Si faltan algunos: Revisa los problemas comunes o consulta la documentación completa en README.md

---

¡Felicidades! Rappi Safe está listo para usar.
