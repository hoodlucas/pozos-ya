from .models import Notificacion

# --- CONTEXT PROCESSOR ---
# Esta función actúa como un inyector global de datos para los templates.
# Al configurarla en settings.py, Django la ejecuta automáticamente en cada petición.
# OBJETIVO: Que la variable {{ notifs_no_leidas }} esté disponible en base.html (navbar)
# siempre, sin tener que calcularla repetidamente en cada una de las Views.

def notificaciones_no_leidas(request):
    if request.user.is_authenticated:
        # Si el usuario está logueado, contamos cuántas notificaciones tiene sin leer
        count = Notificacion.objects.filter(destinatario=request.user, leida=False).count()
        return {"notifs_no_leidas": count}
    return {"notifs_no_leidas": 0}

