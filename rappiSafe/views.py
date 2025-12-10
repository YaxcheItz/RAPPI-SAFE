from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Count, Q, Avg
from django.core.paginator import Paginator
from datetime import timedelta, datetime, date
import json
import uuid

from .models import (
    User, RepartidorProfile, Alerta, Trayectoria, ContactoConfianza,
    Incidente, Bitacora, EstadisticaRiesgo, SolicitudAyudaPsicologica, RutaSegura
)
from .utils import (
    enviar_nueva_alerta, enviar_actualizacion_alerta,
    enviar_actualizacion_ubicacion, serializar_alerta, enviar_notificacion
)


# ==================== AUTENTICACIÓN ====================

def login_view(request):
    """Vista de login"""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None and user.activo:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Credenciales inválidas o cuenta inactiva')

    return render(request, 'registration/login.html')


@login_required
def logout_view(request):
    """Vista de logout"""
    logout(request)
    messages.success(request, 'Sesión cerrada exitosamente')
    return redirect('login')


@login_required
def dashboard(request):
    """
    Vista del dashboard principal que redirige según el rol del usuario
    """
    user = request.user

    if user.rol == 'repartidor':
        return redirect('repartidor_home')
    elif user.rol == 'operador':
        return redirect('operador_dashboard')
    elif user.rol == 'administrador':
        return redirect('admin_dashboard')
    else:
        messages.error(request, 'Rol no reconocido')
        return redirect('login')


# ==================== VERIFICADORES DE ROLES ====================

def es_repartidor(user):
    return user.is_authenticated and user.rol == 'repartidor'


def es_operador(user):
    return user.is_authenticated and user.rol == 'operador'


def es_administrador(user):
    return user.is_authenticated and user.rol == 'administrador'


# ==================== VISTAS REPARTIDOR ====================

def test_sensores(request):
    """Página de prueba de sensores GPS y movimiento (sin login)"""
    return render(request, 'rappiSafe/test_sensores.html')


@login_required
@user_passes_test(es_repartidor, login_url='login')
def repartidor_home(request):
    """Página principal del repartidor con botón de pánico"""
    perfil = request.user.perfil_repartidor
    alertas_activas = Alerta.objects.filter(
        repartidor=request.user,
        estado__in=['pendiente', 'en_atencion']
    ).order_by('-creado_en')

    context = {
        'perfil': perfil,
        'alertas_activas': alertas_activas,
    }
    return render(request, 'rappiSafe/repartidor/home.html', context)


@login_required
@user_passes_test(es_repartidor)
@require_POST
def crear_alerta_panico(request):
    """Crear una alerta de pánico"""
    try:
        data = json.loads(request.body)

        # Crear la alerta
        alerta = Alerta.objects.create(
            repartidor=request.user,
            tipo='panico',
            estado='pendiente',
            latitud=data.get('latitud'),
            longitud=data.get('longitud'),
            nivel_bateria=data.get('bateria'),
            datos_sensores=data.get('datos_sensores', {}),
        )

        # Actualizar el perfil del repartidor
        perfil = request.user.perfil_repartidor
        perfil.estado = 'emergencia'
        perfil.ultima_latitud = data.get('latitud')
        perfil.ultima_longitud = data.get('longitud')
        perfil.nivel_bateria = data.get('bateria')
        perfil.ultima_actualizacion_ubicacion = timezone.now()
        perfil.save()

        # Enviar notificación por WebSocket
        enviar_nueva_alerta(serializar_alerta(alerta))

        # Notificar a contactos de emergencia
        from .utils import notificar_contactos_emergencia
        resultado_notificaciones = notificar_contactos_emergencia(alerta)

        return JsonResponse({
            'success': True,
            'alerta_id': str(alerta.id),
            'mensaje': 'Alerta de pánico activada',
            'contactos_notificados': resultado_notificaciones.get('contactos_notificados', 0),
            'notificaciones_info': f"{resultado_notificaciones.get('contactos_notificados', 0)} contacto(s) notificado(s)"
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@user_passes_test(es_repartidor)
@require_POST
def crear_alerta_accidente(request):
    """Crear una alerta automática por detección de accidente"""
    try:
        data = json.loads(request.body)

        # Crear la alerta
        alerta = Alerta.objects.create(
            repartidor=request.user,
            tipo='accidente',
            estado='pendiente',
            latitud=data.get('latitud'),
            longitud=data.get('longitud'),
            nivel_bateria=data.get('bateria'),
            datos_sensores=data.get('datos_sensores', {}),
        )

        # Actualizar el perfil del repartidor
        perfil = request.user.perfil_repartidor
        perfil.estado = 'emergencia'
        perfil.ultima_latitud = data.get('latitud')
        perfil.ultima_longitud = data.get('longitud')
        perfil.nivel_bateria = data.get('bateria')
        perfil.ultima_actualizacion_ubicacion = timezone.now()
        perfil.save()

        # Enviar notificación por WebSocket
        enviar_nueva_alerta(serializar_alerta(alerta))

        # Notificar a contactos de emergencia
        from .utils import notificar_contactos_emergencia
        resultado_notificaciones = notificar_contactos_emergencia(alerta)

        return JsonResponse({
            'success': True,
            'alerta_id': str(alerta.id),
            'mensaje': 'Alerta de accidente creada',
            'contactos_notificados': resultado_notificaciones.get('contactos_notificados', 0),
            'notificaciones_info': f"{resultado_notificaciones.get('contactos_notificados', 0)} contacto(s) notificado(s)"
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@user_passes_test(es_repartidor)
@require_POST
def cancelar_alerta(request, alerta_id):
    """Cancelar una alerta (marcar como falsa alarma)"""
    try:
        alerta = get_object_or_404(Alerta, id=alerta_id, repartidor=request.user)

        if alerta.estado in ['pendiente', 'en_atencion']:
            alerta.estado = 'falsa_alarma'
            alerta.save()

            # Actualizar perfil del repartidor
            perfil = request.user.perfil_repartidor
            perfil.estado = 'disponible'
            perfil.save()

            # Notificar actualización
            enviar_actualizacion_alerta(serializar_alerta(alerta))

            return JsonResponse({
                'success': True,
                'mensaje': 'Alerta cancelada'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'La alerta no puede ser cancelada'
            }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@user_passes_test(es_repartidor)
@require_POST
def actualizar_ubicacion(request):
    """Actualizar ubicación del repartidor durante una alerta"""
    try:
        data = json.loads(request.body)
        alerta_id = data.get('alerta_id')

        if alerta_id:
            # Enviar actualización por WebSocket
            enviar_actualizacion_ubicacion(
                alerta_id,
                data.get('latitud'),
                data.get('longitud'),
                data.get('precision'),
                data.get('velocidad')
            )

        # Actualizar perfil del repartidor
        perfil = request.user.perfil_repartidor
        perfil.ultima_latitud = data.get('latitud')
        perfil.ultima_longitud = data.get('longitud')
        perfil.ultima_actualizacion_ubicacion = timezone.now()
        perfil.save()

        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@user_passes_test(es_repartidor)
@require_POST
def actualizar_bateria(request):
    """Actualizar nivel de batería del dispositivo"""
    try:
        data = json.loads(request.body)
        perfil = request.user.perfil_repartidor
        perfil.nivel_bateria = data.get('bateria')
        perfil.ultima_actualizacion_bateria = timezone.now()
        perfil.save()

        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@user_passes_test(es_repartidor)
def contactos_confianza_view(request):
    """Ver y gestionar contactos de confianza"""
    contactos = ContactoConfianza.objects.filter(repartidor=request.user).order_by('-creado_en')

    context = {
        'contactos': contactos,
    }
    return render(request, 'rappiSafe/repartidor/contactos.html', context)


@login_required
@user_passes_test(es_repartidor)
@require_POST
def agregar_contacto(request):
    """Agregar un nuevo contacto de confianza"""
    try:
        # Verificar que no tenga más de 3 contactos
        if ContactoConfianza.objects.filter(repartidor=request.user).count() >= 3:
            return JsonResponse({
                'success': False,
                'error': 'Solo puedes tener hasta 3 contactos de confianza'
            }, status=400)

        data = json.loads(request.body)

        contacto = ContactoConfianza.objects.create(
            repartidor=request.user,
            nombre=data.get('nombre'),
            telefono=data.get('telefono'),
            relacion=data.get('relacion', ''),
            telegram_id=data.get('telegram_id', ''),
            email=data.get('email', ''),
            validado=True  # Marcar como validado automáticamente
        )

        return JsonResponse({
            'success': True,
            'mensaje': 'Contacto agregado exitosamente',
            'contacto': {
                'id': contacto.id,
                'nombre': contacto.nombre,
                'telefono': contacto.telefono,
                'relacion': contacto.relacion,
                'validado': contacto.validado
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@user_passes_test(es_repartidor)
@require_POST
def validar_contacto(request, contacto_id):
    """Validar un contacto de confianza"""
    try:
        contacto = ContactoConfianza.objects.get(id=contacto_id, repartidor=request.user)
        contacto.validado = True
        contacto.save()

        return JsonResponse({
            'success': True,
            'mensaje': 'Contacto validado exitosamente'
        })
    except ContactoConfianza.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Contacto no encontrado'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@user_passes_test(es_repartidor)
@require_POST
def eliminar_contacto(request, contacto_id):
    """Eliminar un contacto de confianza"""
    try:
        contacto = ContactoConfianza.objects.get(id=contacto_id, repartidor=request.user)
        contacto.delete()

        return JsonResponse({
            'success': True,
            'mensaje': 'Contacto eliminado exitosamente'
        })
    except ContactoConfianza.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Contacto no encontrado'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@user_passes_test(es_repartidor)
def solicitar_ayuda_psicologica_view(request):
    """Solicitar ayuda psicológica"""
    if request.method == 'POST':
        descripcion = request.POST.get('descripcion')
        urgencia = request.POST.get('urgencia', 5)

        SolicitudAyudaPsicologica.objects.create(
            repartidor=request.user,
            descripcion=descripcion,
            urgencia=urgencia
        )

        messages.success(request, 'Tu solicitud ha sido registrada. Pronto te contactaremos.')
        return redirect('repartidor_home')

    return render(request, 'rappiSafe/repartidor/ayuda_psicologica.html')


@login_required
@user_passes_test(es_repartidor)
def mi_perfil_view(request):
    """Vista de perfil del repartidor"""
    perfil = request.user.perfil_repartidor
    contactos = ContactoConfianza.objects.filter(repartidor=request.user).order_by('-creado_en')

    if request.method == 'POST':
        # Actualizar información del usuario
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.telefono = request.POST.get('telefono', '')
        request.user.save()

        # Actualizar información del perfil
        perfil.tiene_seguro = request.POST.get('tiene_seguro') == 'on'
        perfil.nombre_aseguradora = request.POST.get('nombre_aseguradora', '')
        perfil.numero_poliza = request.POST.get('numero_poliza', '')
        perfil.telefono_aseguradora = request.POST.get('telefono_aseguradora', '')

        vigencia = request.POST.get('vigencia_seguro')
        if vigencia:
            perfil.vigencia_seguro = vigencia
        else:
            perfil.vigencia_seguro = None

        # Actualizar configuración de agitación
        perfil.agitacion_habilitada = request.POST.get('agitacion_habilitada') == 'on'
        sensibilidad = request.POST.get('sensibilidad_agitacion', '15')
        try:
            sensibilidad_val = int(sensibilidad)
            if 10 <= sensibilidad_val <= 30:
                perfil.sensibilidad_agitacion = sensibilidad_val
        except ValueError:
            pass

        # Manejar foto de perfil
        if 'foto' in request.FILES:
            perfil.foto = request.FILES['foto']

        perfil.save()

        messages.success(request, 'Perfil actualizado correctamente')
        return redirect('mi_perfil')

    context = {
        'perfil': perfil,
        'contactos': contactos,
    }
    return render(request, 'rappiSafe/repartidor/mi_perfil.html', context)


@login_required
@user_passes_test(es_repartidor)
def rutas_view(request):
    """Vista de rutas seguras"""
    perfil = request.user.perfil_repartidor

    context = {
        'perfil': perfil,
    }
    return render(request, 'rappiSafe/repartidor/rutas.html', context)


@login_required
@user_passes_test(es_repartidor)
@require_POST
def calcular_rutas(request):
    """Calcular rutas (rápida y seguras) usando API de routing real"""
    try:
        data = json.loads(request.body)
        origen_lat = float(data.get('origen_lat'))
        origen_lon = float(data.get('origen_lon'))
        destino_lat = float(data.get('destino_lat'))
        destino_lon = float(data.get('destino_lon'))

        # Obtener rutas reales usando OSRM
        from .utils import obtener_rutas_alternativas

        resultado = obtener_rutas_alternativas(origen_lat, origen_lon, destino_lat, destino_lon)

        if not resultado.get('success'):
            return JsonResponse({
                'success': False,
                'error': resultado.get('error', 'Error al calcular rutas')
            }, status=400)

        ruta_rapida = resultado['rapida']
        rutas_seguras = resultado['seguras']

        # Preparar datos para respuesta
        ruta_rapida_response = {
            'tipo': 'rapida',
            'distancia': ruta_rapida['distancia'],
            'duracion': ruta_rapida['duracion'],
            'puntuacion_riesgo': round(ruta_rapida['puntuacion_riesgo'], 1),
            'coordenadas': ruta_rapida['coordenadas']
        }

        rutas_seguras_response = [
            {
                'tipo': 'segura',
                'distancia': ruta['distancia'],
                'duracion': ruta['duracion'],
                'puntuacion_riesgo': round(ruta['puntuacion_riesgo'], 1),
                'coordenadas': ruta['coordenadas']
            }
            for ruta in rutas_seguras
        ]

        # Guardar en base de datos
        RutaSegura.objects.create(
            repartidor=request.user,
            origen_lat=origen_lat,
            origen_lon=origen_lon,
            destino_lat=destino_lat,
            destino_lon=destino_lon,
            ruta_rapida=ruta_rapida_response,
            ruta_segura={'rutas': rutas_seguras_response},
            puntuacion_riesgo_rapida=ruta_rapida_response['puntuacion_riesgo'],
            puntuacion_riesgo_segura=rutas_seguras_response[0]['puntuacion_riesgo'],
            seleccionada='rapida'
        )

        return JsonResponse({
            'success': True,
            'rutas': {
                'rapida': ruta_rapida_response,
                'seguras': rutas_seguras_response
            }
        })

    except Exception as e:
        import traceback
        print(f"Error al calcular rutas: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({
            'success': False,
            'error': f'Error al calcular rutas: {str(e)}'
        }, status=400)


# ==================== VISTAS OPERADOR ====================

@login_required
@user_passes_test(es_operador, login_url='login')
def operador_dashboard(request):
    """Dashboard de monitoreo para operadores"""
    alertas_activas = Alerta.objects.filter(
        estado__in=['pendiente', 'en_atencion']
    ).select_related('repartidor').order_by('-creado_en')

    # Incluir solicitudes de ayuda psicológica pendientes
    solicitudes_psicologicas = SolicitudAyudaPsicologica.objects.filter(
        estado__in=['pendiente', 'en_proceso']
    ).select_related('repartidor').order_by('-creado_en')

    context = {
        'alertas_activas': alertas_activas,
        'solicitudes_psicologicas': solicitudes_psicologicas,
        'total_solicitudes_pendientes': solicitudes_psicologicas.filter(estado='pendiente').count(),
    }
    return render(request, 'rappiSafe/operador/dashboard.html', context)


@login_required
@user_passes_test(es_operador)
def ver_alerta(request, alerta_id):
    """Ver detalles de una alerta específica"""
    alerta = get_object_or_404(Alerta, id=alerta_id)
    trayectorias = Trayectoria.objects.filter(alerta=alerta).order_by('timestamp')
    contactos = ContactoConfianza.objects.filter(repartidor=alerta.repartidor)

    # Intentar obtener el incidente asociado
    try:
        incidente = alerta.incidente
        bitacoras = incidente.bitacoras.all().order_by('timestamp')
    except Incidente.DoesNotExist:
        incidente = None
        bitacoras = []

    # Total de solicitudes pendientes para el badge de navegación
    total_solicitudes_pendientes = SolicitudAyudaPsicologica.objects.filter(estado='pendiente').count()

    context = {
        'alerta': alerta,
        'trayectorias': trayectorias,
        'contactos': contactos,
        'incidente': incidente,
        'bitacoras': bitacoras,
        'total_solicitudes_pendientes': total_solicitudes_pendientes,
    }
    return render(request, 'rappiSafe/operador/ver_alerta.html', context)


@login_required
@user_passes_test(es_operador)
def contactar_emergencias(request, alerta_id):
    """Vista para contactar servicios de emergencia"""
    alerta = get_object_or_404(Alerta, id=alerta_id)

    # Total de solicitudes pendientes para el badge de navegación
    total_solicitudes_pendientes = SolicitudAyudaPsicologica.objects.filter(estado='pendiente').count()

    context = {
        'alerta': alerta,
        'total_solicitudes_pendientes': total_solicitudes_pendientes,
    }
    return render(request, 'rappiSafe/operador/emergencias.html', context)


@login_required
@user_passes_test(es_operador)
@require_POST
def atender_alerta(request, alerta_id):
    """Marcar alerta como en atención"""
    try:
        alerta = get_object_or_404(Alerta, id=alerta_id)
        alerta.estado = 'en_atencion'
        alerta.atendido_por = request.user
        alerta.save()

        # Crear incidente si no existe
        if not hasattr(alerta, 'incidente'):
            incidente = Incidente.objects.create(
                alerta=alerta,
                operador=request.user,
                estado='abierto'
            )

            # Registrar en bitácora
            Bitacora.objects.create(
                incidente=incidente,
                operador=request.user,
                accion='Alerta tomada en atención por el operador'
            )

        # Notificar actualización
        enviar_actualizacion_alerta(serializar_alerta(alerta))

        return JsonResponse({
            'success': True,
            'mensaje': 'Alerta atendida'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@user_passes_test(es_operador)
@require_POST
def cerrar_alerta(request, alerta_id):
    """Cerrar una alerta"""
    try:
        data = json.loads(request.body)
        alerta = get_object_or_404(Alerta, id=alerta_id)
        alerta.estado = 'cerrada'
        alerta.save()

        # Actualizar el incidente
        if hasattr(alerta, 'incidente'):
            incidente = alerta.incidente
            incidente.estado = 'cerrado'
            incidente.cerrado_en = timezone.now()
            incidente.tiempo_respuesta = incidente.cerrado_en - incidente.creado_en
            incidente.save()

            # Registrar en bitácora
            Bitacora.objects.create(
                incidente=incidente,
                operador=request.user,
                accion=f"Alerta cerrada. {data.get('notas', '')}"
            )

        # Actualizar perfil del repartidor
        perfil = alerta.repartidor.perfil_repartidor
        perfil.estado = 'disponible'
        perfil.save()

        # Notificar actualización
        enviar_actualizacion_alerta(serializar_alerta(alerta))

        return JsonResponse({
            'success': True,
            'mensaje': 'Alerta cerrada'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@user_passes_test(es_operador)
@require_POST
def agregar_bitacora(request, incidente_id):
    """Agregar entrada a la bitácora de un incidente"""
    try:
        data = json.loads(request.body)
        incidente = get_object_or_404(Incidente, id=incidente_id)

        Bitacora.objects.create(
            incidente=incidente,
            operador=request.user,
            accion=data.get('accion')
        )

        return JsonResponse({
            'success': True,
            'mensaje': 'Entrada agregada a la bitácora'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@user_passes_test(es_operador)
@require_POST
def actualizar_folio_911(request, incidente_id):
    """Actualizar el folio 911 de un incidente"""
    try:
        data = json.loads(request.body)
        incidente = get_object_or_404(Incidente, id=incidente_id)
        incidente.folio_911 = data.get('folio')
        incidente.autoridades_contactadas = True
        incidente.save()

        # Registrar en bitácora
        Bitacora.objects.create(
            incidente=incidente,
            operador=request.user,
            accion=f'Folio 911 registrado: {data.get("folio")}'
        )

        return JsonResponse({
            'success': True,
            'mensaje': 'Folio 911 registrado'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@user_passes_test(es_operador)
def gestionar_solicitudes_psicologicas(request):
    """Vista para gestionar solicitudes de ayuda psicológica"""
    solicitudes = SolicitudAyudaPsicologica.objects.all().select_related('repartidor').order_by('-creado_en')

    context = {
        'solicitudes': solicitudes,
        'total_solicitudes_pendientes': solicitudes.filter(estado='pendiente').count(),
    }
    return render(request, 'rappiSafe/operador/solicitudes_psicologicas.html', context)


@login_required
@user_passes_test(es_operador)
@require_POST
def atender_solicitud_psicologica(request, solicitud_id):
    """Atender una solicitud de ayuda psicológica"""
    try:
        data = json.loads(request.body)
        solicitud = get_object_or_404(SolicitudAyudaPsicologica, id=solicitud_id)

        solicitud.estado = data.get('estado', 'en_proceso')
        solicitud.notas_atencion = data.get('notas_atencion', '')

        if solicitud.estado == 'atendida' and not solicitud.atendido_en:
            solicitud.atendido_en = timezone.now()

        solicitud.save()

        return JsonResponse({
            'success': True,
            'mensaje': 'Solicitud actualizada correctamente'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@user_passes_test(es_operador)
def reportes_operador(request):
    """Vista de reportes para operadores"""
    from datetime import datetime, timedelta
    from django.db.models import Count, Avg, Q
    from django.db.models.functions import TruncDate

    # Obtener rango de fechas (últimos 30 días por defecto)
    fecha_fin = timezone.now()
    fecha_inicio = fecha_fin - timedelta(days=30)

    # Filtros opcionales
    if request.GET.get('fecha_inicio'):
        fecha_inicio = datetime.strptime(request.GET.get('fecha_inicio'), '%Y-%m-%d')
        fecha_inicio = timezone.make_aware(fecha_inicio)
    if request.GET.get('fecha_fin'):
        fecha_fin = datetime.strptime(request.GET.get('fecha_fin'), '%Y-%m-%d')
        fecha_fin = timezone.make_aware(fecha_fin)

    # Alertas en el período
    alertas = Alerta.objects.filter(
        creado_en__range=[fecha_inicio, fecha_fin]
    )

    # Estadísticas generales
    total_alertas = alertas.count()
    alertas_panico = alertas.filter(tipo='panico').count()
    alertas_accidente = alertas.filter(tipo='accidente').count()
    alertas_cerradas = alertas.filter(estado='cerrada').count()
    alertas_pendientes = alertas.filter(estado='pendiente').count()

    # Alertas por día
    alertas_por_dia = alertas.annotate(
        fecha=TruncDate('creado_en')
    ).values('fecha').annotate(
        total=Count('id')
    ).order_by('fecha')

    # Incidentes con tiempo de respuesta
    incidentes = Incidente.objects.filter(
        creado_en__range=[fecha_inicio, fecha_fin],
        tiempo_respuesta__isnull=False
    )

    # Calcular tiempo promedio de respuesta
    if incidentes.exists():
        tiempo_promedio = incidentes.aggregate(
            promedio=Avg('tiempo_respuesta')
        )['promedio']
        if tiempo_promedio:
            tiempo_promedio_minutos = int(tiempo_promedio.total_seconds() / 60)
        else:
            tiempo_promedio_minutos = 0
    else:
        tiempo_promedio_minutos = 0

    # Alertas atendidas por el operador actual
    mis_alertas = alertas.filter(atendido_por=request.user).count()

    # Top 5 operadores con más alertas resueltas
    top_operadores = alertas.filter(
        estado='cerrada',
        atendido_por__isnull=False
    ).values(
        'atendido_por__first_name',
        'atendido_por__last_name',
        'atendido_por__id'
    ).annotate(
        total=Count('id')
    ).order_by('-total')[:5]

    # Solicitudes psicológicas en el período
    solicitudes_psico = SolicitudAyudaPsicologica.objects.filter(
        creado_en__range=[fecha_inicio, fecha_fin]
    )
    total_solicitudes_psico = solicitudes_psico.count()
    solicitudes_psico_atendidas = solicitudes_psico.filter(estado='atendida').count()

    # Total de solicitudes pendientes para el badge de navegación
    total_solicitudes_pendientes = SolicitudAyudaPsicologica.objects.filter(estado='pendiente').count()

    context = {
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'total_alertas': total_alertas,
        'alertas_panico': alertas_panico,
        'alertas_accidente': alertas_accidente,
        'alertas_cerradas': alertas_cerradas,
        'alertas_pendientes': alertas_pendientes,
        'alertas_por_dia': list(alertas_por_dia),
        'tiempo_promedio_minutos': tiempo_promedio_minutos,
        'mis_alertas': mis_alertas,
        'top_operadores': top_operadores,
        'total_solicitudes_psico': total_solicitudes_psico,
        'solicitudes_psico_atendidas': solicitudes_psico_atendidas,
        'total_solicitudes_pendientes': total_solicitudes_pendientes,
    }
    return render(request, 'rappiSafe/operador/reportes.html', context)


@login_required
@user_passes_test(es_operador)
@require_POST
def notificar_contactos_operador(request, alerta_id):
    """Endpoint para notificar contactos de confianza desde el operador"""
    from rappiSafe.utils import notificar_contactos_emergencia

    try:
        alerta = Alerta.objects.select_related('repartidor').get(id=alerta_id)

        # Verificar que la alerta pertenezca a un repartidor
        if not hasattr(alerta.repartidor, 'perfil_repartidor'):
            return JsonResponse({
                'success': False,
                'error': 'El usuario no tiene perfil de repartidor'
            })

        # Llamar a la función de notificaciones
        resultado = notificar_contactos_emergencia(alerta)

        # Actualizar el incidente si existe
        try:
            incidente = Incidente.objects.get(alerta=alerta)
            incidente.contactos_notificados = True
            incidente.save()
        except Incidente.DoesNotExist:
            pass

        return JsonResponse({
            'success': resultado['success'],
            'contactos_notificados': resultado.get('contactos_notificados', 0),
            'notificaciones_fallidas': resultado.get('notificaciones_fallidas', 0),
            'detalles': resultado.get('detalles', [])
        })
    except Alerta.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Alerta no encontrada'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@user_passes_test(es_operador)
def generar_reporte_pdf(request):
    """Generar reporte PDF de alertas"""
    from django.http import HttpResponse
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from datetime import datetime, timedelta
    from django.db.models import Count, Avg
    from django.db.models.functions import TruncDate
    import io

    # Obtener rango de fechas
    fecha_fin = timezone.now()
    fecha_inicio = fecha_fin - timedelta(days=30)

    if request.GET.get('fecha_inicio'):
        fecha_inicio = datetime.strptime(request.GET.get('fecha_inicio'), '%Y-%m-%d')
        fecha_inicio = timezone.make_aware(fecha_inicio)
    if request.GET.get('fecha_fin'):
        fecha_fin = datetime.strptime(request.GET.get('fecha_fin'), '%Y-%m-%d')
        fecha_fin = timezone.make_aware(fecha_fin)

    # Obtener datos
    alertas = Alerta.objects.filter(creado_en__range=[fecha_inicio, fecha_fin])
    total_alertas = alertas.count()
    alertas_panico = alertas.filter(tipo='panico').count()
    alertas_accidente = alertas.filter(tipo='accidente').count()
    alertas_cerradas = alertas.filter(estado='cerrada').count()
    alertas_pendientes = alertas.filter(estado='pendiente').count()

    # Crear el PDF en memoria
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#dc2626'),
        spaceAfter=30,
        alignment=TA_CENTER
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#dc2626'),
        spaceAfter=12,
        spaceBefore=12
    )

    # Título
    elements.append(Paragraph("Reporte de Alertas - RappiSafe", title_style))
    elements.append(Spacer(1, 0.2*inch))

    # Período
    periodo_text = f"Período: {fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}"
    elements.append(Paragraph(periodo_text, styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))

    # Estadísticas generales
    elements.append(Paragraph("Estadísticas Generales", heading_style))
    data_stats = [
        ['Métrica', 'Valor'],
        ['Total de Alertas', str(total_alertas)],
        ['Alertas de Pánico', str(alertas_panico)],
        ['Alertas de Accidente', str(alertas_accidente)],
        ['Alertas Cerradas', str(alertas_cerradas)],
        ['Alertas Pendientes', str(alertas_pendientes)],
    ]

    table_stats = Table(data_stats, colWidths=[3*inch, 2*inch])
    table_stats.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dc2626')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table_stats)
    elements.append(Spacer(1, 0.3*inch))

    # Top Repartidores
    elements.append(Paragraph("Top 5 Repartidores con Más Alertas", heading_style))
    top_repartidores = alertas.values(
        'repartidor__first_name',
        'repartidor__last_name'
    ).annotate(
        total=Count('id')
    ).order_by('-total')[:5]

    data_top = [['Posición', 'Repartidor', 'Total Alertas']]
    for idx, rep in enumerate(top_repartidores, 1):
        nombre = f"{rep['repartidor__first_name']} {rep['repartidor__last_name']}"
        data_top.append([str(idx), nombre, str(rep['total'])])

    if len(data_top) > 1:
        table_top = Table(data_top, colWidths=[1*inch, 3*inch, 1.5*inch])
        table_top.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dc2626')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(table_top)
    else:
        elements.append(Paragraph("No hay datos disponibles", styles['Normal']))

    elements.append(Spacer(1, 0.3*inch))

    # Pie de página
    elements.append(Spacer(1, 0.5*inch))
    footer_text = f"Generado el {timezone.now().strftime('%d/%m/%Y %H:%M:%S')} por {request.user.get_full_name()}"
    elements.append(Paragraph(footer_text, styles['Normal']))

    # Construir PDF
    doc.build(elements)

    # Preparar respuesta
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    filename = f"reporte_alertas_{fecha_inicio.strftime('%Y%m%d')}_{fecha_fin.strftime('%Y%m%d')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    return response


@login_required
@user_passes_test(es_operador)
def lista_repartidores(request):
    """Vista para listar todos los repartidores"""
    repartidores = User.objects.filter(
        rol='repartidor',
        is_active=True
    ).select_related('perfil_repartidor').order_by('first_name', 'last_name')

    # Estadísticas por repartidor
    repartidores_data = []
    for repartidor in repartidores:
        # Contar alertas
        total_alertas = Alerta.objects.filter(repartidor=repartidor).count()
        alertas_activas = Alerta.objects.filter(
            repartidor=repartidor,
            estado__in=['pendiente', 'en_atencion']
        ).count()
        ultima_alerta = Alerta.objects.filter(repartidor=repartidor).order_by('-creado_en').first()

        # Obtener perfil
        try:
            perfil = repartidor.perfil_repartidor
            estado = perfil.estado
            ultima_ubicacion = {
                'lat': perfil.ultima_latitud,
                'lon': perfil.ultima_longitud,
                'fecha': perfil.ultima_actualizacion_ubicacion
            } if perfil.ultima_latitud else None
            nivel_bateria = perfil.nivel_bateria
        except:
            estado = 'offline'
            ultima_ubicacion = None
            nivel_bateria = None

        # Contactos de confianza
        contactos = ContactoConfianza.objects.filter(repartidor=repartidor)

        repartidores_data.append({
            'repartidor': repartidor,
            'estado': estado,
            'total_alertas': total_alertas,
            'alertas_activas': alertas_activas,
            'ultima_alerta': ultima_alerta,
            'ultima_ubicacion': ultima_ubicacion,
            'nivel_bateria': nivel_bateria,
            'contactos': contactos,
        })

    # Total de solicitudes pendientes para el badge de navegación
    total_solicitudes_pendientes = SolicitudAyudaPsicologica.objects.filter(estado='pendiente').count()

    context = {
        'repartidores_data': repartidores_data,
        'total_solicitudes_pendientes': total_solicitudes_pendientes,
    }
    return render(request, 'rappiSafe/operador/repartidores.html', context)


@login_required
@user_passes_test(es_operador)
def operador_perfil_view(request):
    """Vista de perfil del operador"""
    # Total de solicitudes pendientes para el badge de navegación
    total_solicitudes_pendientes = SolicitudAyudaPsicologica.objects.filter(estado='pendiente').count()

    if request.method == 'POST':
        # Actualizar información del usuario
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.telefono = request.POST.get('telefono', '')
        request.user.save()

        messages.success(request, 'Perfil actualizado correctamente')
        return redirect('operador_perfil')

    # Estadísticas del operador
    alertas_atendidas = Alerta.objects.filter(atendido_por=request.user).count()
    alertas_cerradas = Alerta.objects.filter(
        atendido_por=request.user,
        estado='cerrada'
    ).count()

    # Últimas alertas atendidas
    ultimas_alertas = Alerta.objects.filter(
        atendido_por=request.user
    ).select_related('repartidor').order_by('-actualizado_en')[:5]

    context = {
        'alertas_atendidas': alertas_atendidas,
        'alertas_cerradas': alertas_cerradas,
        'ultimas_alertas': ultimas_alertas,
        'total_solicitudes_pendientes': total_solicitudes_pendientes,
    }
    return render(request, 'rappiSafe/operador/perfil.html', context)


# ==================== VISTAS ADMINISTRADOR ====================

@login_required
@user_passes_test(es_administrador, login_url='login')
def admin_dashboard(request):
    """Dashboard principal del administrador"""
    # Estadísticas generales
    total_usuarios = User.objects.filter(activo=True).count()
    total_repartidores = User.objects.filter(rol='repartidor', activo=True).count()
    total_operadores = User.objects.filter(rol='operador', activo=True).count()

    # Alertas del mes actual
    inicio_mes = timezone.now().replace(day=1, hour=0, minute=0, second=0)
    alertas_mes = Alerta.objects.filter(creado_en__gte=inicio_mes).count()

    # Alertas por tipo
    alertas_por_tipo = Alerta.objects.values('tipo').annotate(total=Count('id'))

    context = {
        'total_usuarios': total_usuarios,
        'total_repartidores': total_repartidores,
        'total_operadores': total_operadores,
        'alertas_mes': alertas_mes,
        'alertas_por_tipo': alertas_por_tipo,
    }
    return render(request, 'rappiSafe/admin/dashboard.html', context)


@login_required
@user_passes_test(es_administrador)
def gestionar_usuarios(request):
    """Gestionar usuarios del sistema"""
    usuarios = User.objects.all().order_by('-date_joined')

    # Filtros
    rol_filtro = request.GET.get('rol')
    if rol_filtro:
        usuarios = usuarios.filter(rol=rol_filtro)

    estado_filtro = request.GET.get('estado')
    if estado_filtro == 'activo':
        usuarios = usuarios.filter(activo=True)
    elif estado_filtro == 'inactivo':
        usuarios = usuarios.filter(activo=False)

    # Paginación
    paginator = Paginator(usuarios, 20)
    page = request.GET.get('page')
    usuarios = paginator.get_page(page)

    context = {
        'usuarios': usuarios,
    }
    return render(request, 'rappiSafe/admin/usuarios.html', context)


@login_required
@user_passes_test(es_administrador)
def estadisticas_view(request):
    """Vista de estadísticas y reportes"""
    # Rango de fechas (últimos 30 días por defecto)
    fecha_fin = timezone.now().date()
    fecha_inicio = fecha_fin - timedelta(days=30)

    if request.GET.get('fecha_inicio'):
        fecha_inicio = datetime.strptime(request.GET.get('fecha_inicio'), '%Y-%m-%d').date()
    if request.GET.get('fecha_fin'):
        fecha_fin = datetime.strptime(request.GET.get('fecha_fin'), '%Y-%m-%d').date()

    # Estadísticas de alertas
    alertas = Alerta.objects.filter(
        creado_en__date__gte=fecha_inicio,
        creado_en__date__lte=fecha_fin
    )

    total_alertas = alertas.count()
    alertas_panico = alertas.filter(tipo='panico').count()
    alertas_accidente = alertas.filter(tipo='accidente').count()

    # Alertas por estado
    alertas_por_estado = alertas.values('estado').annotate(total=Count('id'))

    # Zonas de riesgo
    zonas_riesgo = EstadisticaRiesgo.objects.all().order_by('-puntuacion_riesgo')[:10]

    context = {
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'total_alertas': total_alertas,
        'alertas_panico': alertas_panico,
        'alertas_accidente': alertas_accidente,
        'alertas_por_estado': alertas_por_estado,
        'zonas_riesgo': zonas_riesgo,
    }
    return render(request, 'rappiSafe/admin/estadisticas.html', context)


@login_required
@user_passes_test(es_repartidor)
def historial_view(request):
    """Vista de historial de alertas y solicitudes de ayuda del repartidor"""
    # Obtener todas las alertas del repartidor ordenadas por fecha
    alertas = Alerta.objects.filter(repartidor=request.user).order_by('-creado_en')

    # Obtener todas las solicitudes de ayuda psicológica
    solicitudes_ayuda = SolicitudAyudaPsicologica.objects.filter(
        repartidor=request.user
    ).order_by('-creado_en')

    # Paginación para alertas
    paginator_alertas = Paginator(alertas, 10)
    page_alertas = request.GET.get('page_alertas', 1)
    alertas_page = paginator_alertas.get_page(page_alertas)

    # Paginación para solicitudes
    paginator_solicitudes = Paginator(solicitudes_ayuda, 10)
    page_solicitudes = request.GET.get('page_solicitudes', 1)
    solicitudes_page = paginator_solicitudes.get_page(page_solicitudes)

    # Estadísticas rápidas
    total_alertas = alertas.count()
    alertas_resueltas = alertas.filter(estado='resuelta').count()
    alertas_panico = alertas.filter(tipo='panico').count()
    alertas_accidente = alertas.filter(tipo='accidente').count()
    total_solicitudes = solicitudes_ayuda.count()
    solicitudes_atendidas = solicitudes_ayuda.filter(estado='atendida').count()

    context = {
        'alertas': alertas_page,
        'solicitudes_ayuda': solicitudes_page,
        'total_alertas': total_alertas,
        'alertas_resueltas': alertas_resueltas,
        'alertas_panico': alertas_panico,
        'alertas_accidente': alertas_accidente,
        'total_solicitudes': total_solicitudes,
        'solicitudes_atendidas': solicitudes_atendidas,
    }

    return render(request, 'rappiSafe/repartidor/historial.html', context)


def register_view(request):
    """Vista de registro de nuevos usuarios repartidores"""
    import logging
    logger = logging.getLogger(__name__)

    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        # Obtener datos del formulario y hacer trim
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        numero_identificacion = request.POST.get('numero_identificacion', '').strip()

        logger.info(f'Intento de registro - Username: {username}, Email: {email}')

        # Validaciones
        errors = []

        # Validar que todos los campos estén presentes
        if not all([username, email, password, password2, first_name, last_name, telefono, numero_identificacion]):
            errors.append('Todos los campos son obligatorios')
            logger.warning('Registro fallido: campos vacíos')

        # Solo validar unicidad si los campos tienen valores
        if username:
            if User.objects.filter(username__iexact=username).exists():
                errors.append('El nombre de usuario ya está en uso')
                logger.warning(f'Registro fallido: username {username} ya existe')

        if email:
            if User.objects.filter(email__iexact=email).exists():
                errors.append('El correo electrónico ya está registrado')
                logger.warning(f'Registro fallido: email {email} ya existe')

        if numero_identificacion:
            if RepartidorProfile.objects.filter(numero_identificacion__iexact=numero_identificacion).exists():
                errors.append('El número de identificación ya está registrado')
                logger.warning(f'Registro fallido: identificación {numero_identificacion} ya existe')

        # Validaciones de contraseña solo si hay contraseñas
        if password or password2:
            if password != password2:
                errors.append('Las contraseñas no coinciden')

            if len(password) < 8:
                errors.append('La contraseña debe tener al menos 8 caracteres')

            if not any(char.isdigit() for char in password):
                errors.append('La contraseña debe contener al menos un número')

            if not any(char.isalpha() for char in password):
                errors.append('La contraseña debe contener al menos una letra')

        # Si hay errores, mostrarlos
        if errors:
            for error in errors:
                messages.error(request, error)
            logger.warning(f'Registro fallido con errores: {errors}')
            return render(request, 'registration/register.html')

        try:
            # Crear el usuario
            logger.info(f'Creando usuario {username}...')
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                telefono=telefono,
                rol='repartidor',
                activo=True
            )
            logger.info(f'Usuario {username} creado exitosamente con ID {user.id}')

            # Crear el perfil de repartidor
            logger.info(f'Creando perfil de repartidor para usuario {username}...')
            RepartidorProfile.objects.create(
                user=user,
                numero_identificacion=numero_identificacion
            )
            logger.info(f'Perfil de repartidor creado exitosamente para {username}')

            messages.success(request, 'Cuenta creada exitosamente. Por favor inicia sesión.')
            return redirect('login')

        except Exception as e:
            logger.error(f'Error al crear cuenta para {username}: {str(e)}', exc_info=True)

            # Verificar si es un error de constraint único
            error_msg = str(e).lower()
            if 'unique' in error_msg or 'unique constraint' in error_msg:
                if 'email' in error_msg:
                    messages.error(request, 'El correo electrónico ya está registrado.')
                elif 'username' in error_msg:
                    messages.error(request, 'El nombre de usuario ya está en uso.')
                elif 'numero_identificacion' in error_msg:
                    messages.error(request, 'El número de identificación ya está registrado.')
                else:
                    messages.error(request, 'Ya existe un registro con estos datos. Por favor verifica tu información.')
            else:
                messages.error(request, f'Error al crear la cuenta: {str(e)}')

            # Si el usuario se creó pero falló el perfil, eliminarlo
            try:
                if 'user' in locals() and user.pk:
                    logger.warning(f'Eliminando usuario {username} debido a error en creación de perfil')
                    user.delete()
            except Exception as delete_error:
                logger.error(f'Error al eliminar usuario fallido: {str(delete_error)}')

            return render(request, 'registration/register.html')

    return render(request, 'registration/register.html')
