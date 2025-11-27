from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from functools import wraps

def solo_municipio(view_func):
    """
    Decorador que permite acceder solo a usuarios logueados
    cuyo perfil tenga rol = 'municipio'.
    """
    @login_required
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Si no tiene perfil o no es municipio -> prohibido
        if not hasattr(request.user, "perfil") or request.user.perfil.rol != "municipio":
            return HttpResponseForbidden("No tenés permisos para ver esta página.")
        return view_func(request, *args, **kwargs)

    return _wrapped_view