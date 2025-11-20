from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Bache
from .forms import BacheForm
from django.contrib.auth import logout

# Create your views here.

def lista_baches(request):
    # 1) Leer todos los baches de la base, ordenados del más nuevo al más viejo
    baches = Bache.objects.all().order_by('-fecha_creacion')

    # 2) Pasar esos baches al template 'baches/lista_baches.html'
    return render(request, 'baches/lista_baches.html', {'baches': baches})


# CREAR
def crear_bache(request):
    if request.method == 'POST':
        form = BacheForm(request.POST)
        if form.is_valid():
            #  Todavía no guardo en la BD
            bache = form.save(commit=False)
            
            #  Si el usuario está logueado, lo asocio
            if request.user.is_authenticated:
                bache.vecino = request.user
            
            #  Ahora sí guardo en la tabla baches_bache
            bache.save()
            return redirect('lista_baches')
    else:
        # request.method == 'GET' → el usuario entra por primera vez
        form = BacheForm()

    return render(request, 'baches/crear_bache.html', {'form': form})


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

