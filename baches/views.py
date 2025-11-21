from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Bache
from .forms import BacheForm
from django.contrib.auth import logout
import json
from django.core.serializers.json import DjangoJSONEncoder


#CARGAR DATOS EN PRINCIPAL
def lista_baches(request):
    # Filtros desde la querystring (?estado=...&severidad=...&mios=1)
    estado = request.GET.get("estado", "")
    severidad = request.GET.get("severidad", "")
    mios = request.GET.get("mios", "")

    # Query
    baches_qs = Bache.objects.all().order_by("-fecha_creacion")

    # Aplicamos filtros si vinieron
    if estado:
        baches_qs = baches_qs.filter(estado=estado)

    if severidad:
        baches_qs = baches_qs.filter(severidad=severidad)
    
    if mios and request.user.is_authenticated:
        baches_qs = baches_qs.filter(vecino=request.user)

    # Para la tabla usamos el queryset filtrado
    baches = baches_qs
    # Para el mapa, del mismo queryset filtrado tomamos solo los que tienen coords
    baches_con_coords = (
        baches_qs
        .exclude(latitud__isnull=True)
        .exclude(longitud__isnull=True)
    )
    # Pasamos datos simples a JS
    baches_data = [
        {
            "id": b.id,
            "titulo": b.titulo,
            "latitud": b.latitud,
            "longitud": b.longitud,
            "severidad": b.severidad,
            "estado": b.estado,
            "imagen_url": b.imagen.url if b.imagen else None,
        }
        for b in baches_con_coords
    ]
    # Enviamos también los filtros actuales para mantenerlos seleccionados en la UI
    return render(
        request,
        "baches/lista_baches.html",
        {
            "baches": baches,
            "baches_data": baches_data,
            "estado_actual": estado,
            "severidad_actual": severidad,
            "mios_actual": mios,
        }
    )


# CREAR
@login_required
def crear_bache(request):
    if request.method == "POST":
        form = BacheForm(request.POST, request.FILES)
        if form.is_valid():
            bache = form.save(commit=False)
            bache.vecino = request.user
            bache.save()
            return redirect("lista_baches")
    else:
        form = BacheForm()
    return render(request, "baches/crear_bache.html", {"form": form})


# Página de la municipalidad
@login_required
def panel_municipio(request):
    # Solo permitir usuarios con perfil de municipio
    if not hasattr(request.user, 'perfil') or request.user.perfil.rol != 'municipio':
        return HttpResponseForbidden("No tenés permisos para ver esta página.")

    # Si llega un POST, actualizar estado de un bache
    if request.method == 'POST':
        bache_id = request.POST.get('bache_id')
        nuevo_estado = request.POST.get('estado')

        if bache_id and nuevo_estado:
            try:
                bache = Bache.objects.get(id=bache_id)
                # Validar que el estado exista en las opciones del modelo
                estados_validos = dict(Bache.ESTADO_CHOICES).keys()
                if nuevo_estado in estados_validos:
                    bache.estado = nuevo_estado
                    bache.save()
            except Bache.DoesNotExist:
                pass

        return redirect('panel_municipio')

    # Si es GET, mostrar todos los baches
    baches = Bache.objects.all().order_by('-fecha_creacion')
    return render(request, 'baches/panel_municipio.html', { 'baches': baches, 'ESTADO_CHOICES': Bache.ESTADO_CHOICES,})


# LOGOUT
def logout_view(request):
    logout(request)  # borra la sesión del usuario
    return redirect('lista_baches')  # siempre vuelve al inicio



def detalle_bache(request, pk):
    bache = get_object_or_404(Bache, pk=pk)

    # si querés luego, acá controlamos permisos por rol
    # por ahora cualquiera puede ver el detalle

    return render(request, "baches/detalle_bache.html", {"bache": bache})



