import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from .models import Alerta, Trayectoria, User


class AlertasConsumer(AsyncWebsocketConsumer):
    """
    Consumer para transmitir alertas en tiempo real a los operadores
    """
    async def connect(self):
        self.group_name = 'alertas'

        # Verificar que el usuario esté autenticado y sea operador o admin
        if self.scope["user"] == AnonymousUser():
            await self.close()
            return

        user = self.scope["user"]
        if user.rol not in ['operador', 'administrador']:
            await self.close()
            return

        # Unirse al grupo de alertas
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Salir del grupo de alertas
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Este consumer no recibe mensajes, solo transmite
        pass

    async def nueva_alerta(self, event):
        """
        Enviar nueva alerta a todos los operadores conectados
        """
        await self.send(text_data=json.dumps({
            'tipo': 'nueva_alerta',
            'alerta': event['alerta']
        }))

    async def actualizar_alerta(self, event):
        """
        Enviar actualización de alerta
        """
        await self.send(text_data=json.dumps({
            'tipo': 'actualizar_alerta',
            'alerta': event['alerta']
        }))


class UbicacionConsumer(AsyncWebsocketConsumer):
    """
    Consumer para transmitir actualizaciones de ubicación en tiempo real
    """
    async def connect(self):
        self.alerta_id = self.scope['url_route']['kwargs']['alerta_id']
        self.group_name = f'ubicacion_{self.alerta_id}'

        # Verificar autenticación
        if self.scope["user"] == AnonymousUser():
            await self.close()
            return

        # Unirse al grupo de ubicación
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Salir del grupo de ubicación
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """
        Recibir actualización de ubicación del repartidor
        """
        try:
            data = json.loads(text_data)

            if data.get('tipo') == 'ubicacion':
                # Guardar la trayectoria en la base de datos
                await self.guardar_trayectoria(
                    self.alerta_id,
                    data.get('latitud'),
                    data.get('longitud'),
                    data.get('precision'),
                    data.get('velocidad')
                )

                # Transmitir a todos en el grupo
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        'type': 'actualizar_ubicacion',
                        'latitud': data.get('latitud'),
                        'longitud': data.get('longitud'),
                        'precision': data.get('precision'),
                        'velocidad': data.get('velocidad'),
                        'timestamp': data.get('timestamp')
                    }
                )
        except json.JSONDecodeError:
            pass

    async def actualizar_ubicacion(self, event):
        """
        Enviar actualización de ubicación a todos los clientes
        """
        await self.send(text_data=json.dumps({
            'tipo': 'ubicacion',
            'latitud': event['latitud'],
            'longitud': event['longitud'],
            'precision': event.get('precision'),
            'velocidad': event.get('velocidad'),
            'timestamp': event.get('timestamp')
        }))

    @database_sync_to_async
    def guardar_trayectoria(self, alerta_id, latitud, longitud, precision, velocidad):
        """
        Guardar punto de trayectoria en la base de datos
        """
        try:
            alerta = Alerta.objects.get(id=alerta_id)
            Trayectoria.objects.create(
                alerta=alerta,
                latitud=latitud,
                longitud=longitud,
                precision=precision,
                velocidad=velocidad
            )
        except Alerta.DoesNotExist:
            pass


class MonitoreoConsumer(AsyncWebsocketConsumer):
    """
    Consumer para el dashboard de monitoreo de operadores
    Recibe todas las actualizaciones: alertas, ubicaciones, estados
    """
    async def connect(self):
        self.group_name = 'monitoreo'

        # Verificar que el usuario esté autenticado y sea operador o admin
        if self.scope["user"] == AnonymousUser():
            await self.close()
            return

        user = self.scope["user"]
        if user.rol not in ['operador', 'administrador']:
            await self.close()
            return

        # Unirse al grupo de monitoreo
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Salir del grupo de monitoreo
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Este consumer puede recibir comandos
        try:
            data = json.loads(text_data)
            tipo = data.get('tipo')

            if tipo == 'solicitar_estado':
                # Enviar estado actual del sistema
                estado = await self.obtener_estado_sistema()
                await self.send(text_data=json.dumps({
                    'tipo': 'estado_sistema',
                    'data': estado
                }))
        except json.JSONDecodeError:
            pass

    async def notificacion(self, event):
        """
        Enviar notificación general
        """
        await self.send(text_data=json.dumps({
            'tipo': 'notificacion',
            'mensaje': event['mensaje'],
            'nivel': event.get('nivel', 'info')
        }))

    async def nueva_alerta_monitoreo(self, event):
        """
        Enviar nueva alerta al dashboard de monitoreo
        """
        await self.send(text_data=json.dumps({
            'tipo': 'nueva_alerta',
            'alerta': event['alerta']
        }))

    async def actualizar_estado_repartidor(self, event):
        """
        Actualizar estado de un repartidor en el mapa
        """
        await self.send(text_data=json.dumps({
            'tipo': 'estado_repartidor',
            'repartidor_id': event['repartidor_id'],
            'estado': event['estado'],
            'latitud': event.get('latitud'),
            'longitud': event.get('longitud')
        }))

    @database_sync_to_async
    def obtener_estado_sistema(self):
        """
        Obtener estado actual del sistema
        """
        alertas_activas = Alerta.objects.filter(
            estado__in=['pendiente', 'en_atencion']
        ).count()

        return {
            'alertas_activas': alertas_activas,
            'timestamp': None  # Se llenará en el cliente
        }
