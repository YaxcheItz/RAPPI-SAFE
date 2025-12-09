from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json


def enviar_nueva_alerta(alerta_dict):
    """
    Enviar nueva alerta a todos los operadores conectados
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'alertas',
        {
            'type': 'nueva_alerta',
            'alerta': alerta_dict
        }
    )
    # También enviar al grupo de monitoreo
    async_to_sync(channel_layer.group_send)(
        'monitoreo',
        {
            'type': 'nueva_alerta_monitoreo',
            'alerta': alerta_dict
        }
    )


def enviar_actualizacion_alerta(alerta_dict):
    """
    Enviar actualización de alerta existente
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'alertas',
        {
            'type': 'actualizar_alerta',
            'alerta': alerta_dict
        }
    )


def enviar_actualizacion_ubicacion(alerta_id, latitud, longitud, precision=None, velocidad=None):
    """
    Enviar actualización de ubicación para una alerta específica
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'ubicacion_{alerta_id}',
        {
            'type': 'actualizar_ubicacion',
            'latitud': str(latitud),
            'longitud': str(longitud),
            'precision': precision,
            'velocidad': velocidad,
            'timestamp': None  # Se llenará en el cliente
        }
    )


def enviar_notificacion(mensaje, nivel='info'):
    """
    Enviar notificación general al dashboard de monitoreo
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'monitoreo',
        {
            'type': 'notificacion',
            'mensaje': mensaje,
            'nivel': nivel
        }
    )


def enviar_estado_repartidor(repartidor_id, estado, latitud=None, longitud=None):
    """
    Enviar actualización de estado de un repartidor
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'monitoreo',
        {
            'type': 'actualizar_estado_repartidor',
            'repartidor_id': repartidor_id,
            'estado': estado,
            'latitud': str(latitud) if latitud else None,
            'longitud': str(longitud) if longitud else None
        }
    )


def serializar_alerta(alerta):
    """
    Serializar una alerta para envío por WebSocket
    """
    return {
        'id': str(alerta.id),
        'repartidor': {
            'id': alerta.repartidor.id,
            'nombre': alerta.repartidor.get_full_name(),
            'telefono': alerta.repartidor.telefono,
        },
        'tipo': alerta.tipo,
        'estado': alerta.estado,
        'latitud': str(alerta.latitud),
        'longitud': str(alerta.longitud),
        'nivel_bateria': alerta.nivel_bateria,
        'creado_en': alerta.creado_en.isoformat(),
        'datos_sensores': alerta.datos_sensores,
    }
