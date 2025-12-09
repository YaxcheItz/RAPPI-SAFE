from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, RepartidorProfile, Alerta, Trayectoria, ContactoConfianza,
    Incidente, Bitacora, EstadisticaRiesgo, SolicitudAyudaPsicologica, RutaSegura
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'rol', 'activo', 'date_joined')
    list_filter = ('rol', 'activo', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'telefono')

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Información Adicional', {'fields': ('rol', 'activo', 'telefono')}),
    )


@admin.register(RepartidorProfile)
class RepartidorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'numero_identificacion', 'estado', 'nivel_bateria', 'ultima_actualizacion_ubicacion')
    list_filter = ('estado',)
    search_fields = ('user__username', 'user__email', 'numero_identificacion')
    readonly_fields = ('ultima_actualizacion_ubicacion', 'ultima_actualizacion_bateria')


@admin.register(Alerta)
class AlertaAdmin(admin.ModelAdmin):
    list_display = ('id', 'repartidor', 'tipo', 'estado', 'nivel_bateria', 'creado_en', 'atendido_por')
    list_filter = ('tipo', 'estado', 'creado_en')
    search_fields = ('repartidor__username', 'repartidor__email', 'id')
    readonly_fields = ('id', 'creado_en', 'actualizado_en')
    date_hierarchy = 'creado_en'


@admin.register(Trayectoria)
class TrayectoriaAdmin(admin.ModelAdmin):
    list_display = ('alerta', 'latitud', 'longitud', 'velocidad', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('alerta__id', 'alerta__repartidor__username')
    readonly_fields = ('timestamp',)


@admin.register(ContactoConfianza)
class ContactoConfianzaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'telefono', 'repartidor', 'relacion', 'validado', 'creado_en')
    list_filter = ('validado', 'creado_en')
    search_fields = ('nombre', 'telefono', 'repartidor__username')


@admin.register(Incidente)
class IncidenteAdmin(admin.ModelAdmin):
    list_display = ('id', 'alerta', 'operador', 'estado', 'folio_911', 'creado_en', 'cerrado_en')
    list_filter = ('estado', 'contactos_notificados', 'autoridades_contactadas', 'creado_en')
    search_fields = ('folio_911', 'alerta__id', 'alerta__repartidor__username')
    readonly_fields = ('creado_en',)
    date_hierarchy = 'creado_en'


@admin.register(Bitacora)
class BitacoraAdmin(admin.ModelAdmin):
    list_display = ('incidente', 'operador', 'accion', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('incidente__id', 'operador__username', 'accion')
    readonly_fields = ('timestamp',)


@admin.register(EstadisticaRiesgo)
class EstadisticaRiesgoAdmin(admin.ModelAdmin):
    list_display = ('nombre_zona', 'puntuacion_riesgo', 'total_alertas', 'periodo_inicio', 'periodo_fin', 'ultima_actualizacion')
    list_filter = ('ultima_actualizacion', 'periodo_inicio')
    search_fields = ('nombre_zona',)
    readonly_fields = ('ultima_actualizacion',)


@admin.register(SolicitudAyudaPsicologica)
class SolicitudAyudaPsicologicaAdmin(admin.ModelAdmin):
    list_display = ('id', 'repartidor', 'estado', 'urgencia', 'creado_en', 'atendido_en')
    list_filter = ('estado', 'urgencia', 'creado_en')
    search_fields = ('repartidor__username', 'repartidor__email', 'descripcion')
    readonly_fields = ('creado_en',)
    date_hierarchy = 'creado_en'


@admin.register(RutaSegura)
class RutaSeguraAdmin(admin.ModelAdmin):
    list_display = ('repartidor', 'seleccionada', 'puntuacion_riesgo_rapida', 'puntuacion_riesgo_segura', 'creado_en')
    list_filter = ('seleccionada', 'creado_en')
    search_fields = ('repartidor__username',)
    readonly_fields = ('creado_en',)
