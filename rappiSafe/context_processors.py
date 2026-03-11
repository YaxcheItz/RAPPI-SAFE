from .models import SolicitudAyudaPsicologica

def operador_context(request):
    """
    Proporciona datos globales para las plantillas del operador,
    como el conteo de solicitudes pendientes para el badge de navegación.
    """
    if request.user.is_authenticated and request.user.rol == 'operador':
        return {
            'total_solicitudes_pendientes': SolicitudAyudaPsicologica.objects.filter(estado='pendiente').count()
        }
    return {}
