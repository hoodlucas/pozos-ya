from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Bache, HistorialBache, Notificacion, Perfil
from .forms import BacheForm, RegistroForm
from django.http import HttpResponse
from django.contrib.auth import logout
import json
from django.core.serializers.json import DjangoJSONEncoder
from .decorators import solo_municipio
from django.utils import timezone
from django.db.models import Q
from django.urls import reverse
from django.contrib.auth import login
import csv
from django.db.models import Count
from django.contrib.auth.views import LoginView
from django.contrib import messages

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



# MUNICIPIO
@login_required
def panel_municipio(request):
    # 0) Seguridad por rol
    if not hasattr(request.user, "perfil") or request.user.perfil.rol != "municipio":
        return HttpResponseForbidden("No tenés permisos para ver esta página.")

    if request.method == "POST":

        # 1) Recorremos todos los inputs del POST buscando estado_{id}
        for key, value in request.POST.items():
            if not key.startswith("estado_"):
                continue

            partes = key.split("_", 1)
            if len(partes) != 2 or not partes[1].isdigit():
                continue  # clave malformada

            bache_id = int(partes[1])
            nuevo_estado = (value or "").strip()

            # comentario_{id} correspondiente
            comentario_key = f"comentario_{bache_id}"
            nuevo_comentario = (request.POST.get(comentario_key) or "").strip()

            try:
                bache = Bache.objects.get(id=bache_id)
            except Bache.DoesNotExist:
                continue

            # 2) Guardamos valores anteriores
            estado_anterior = bache.estado
            comentario_anterior = getattr(bache, "comentario_municipio", "") or ""

            hubo_cambio = False

            # 3) Estado nuevo
            if nuevo_estado and nuevo_estado != estado_anterior:
                bache.estado = nuevo_estado
                hubo_cambio = True

                # fecha_resolucion opcional
                if hasattr(bache, "fecha_resolucion"):
                    if nuevo_estado == "resuelto":
                        bache.fecha_resolucion = timezone.now()
                    else:
                        bache.fecha_resolucion = None

            # 4) Comentario nuevo (si existe el campo)
            if hasattr(bache, "comentario_municipio"):
                if nuevo_comentario != comentario_anterior:
                    bache.comentario_municipio = nuevo_comentario
                    hubo_cambio = True

            # 5) Si no hubo cambios reales, pasamos al siguiente
            if not hubo_cambio:
                continue

            # 6) Guardamos el bache
            bache.save()

            # 7) Historial
            HistorialBache.objects.create(
                bache=bache,
                actor=request.user,
                estado_anterior=estado_anterior,
                estado_nuevo=bache.estado,
                comentario_anterior=comentario_anterior,
                comentario_nuevo=getattr(bache, "comentario_municipio", "") or "",
            )

            # 8) Notificación al vecino (si existe)
            if bache.vecino:
                # definimos tipo/mensaje según qué cambió
                cambio_estado = (bache.estado != estado_anterior)
                cambio_coment = (
                    hasattr(bache, "comentario_municipio")
                    and nuevo_comentario != comentario_anterior
                    and nuevo_comentario != ""
                )

                if cambio_estado and cambio_coment:
                    tipo = "mixto"
                    mensaje = (
                        f"Tu reclamo '{bache.titulo}' cambió a {bache.get_estado_display()} "
                        f"y el municipio dejó un comentario."
                    )
                elif cambio_estado:
                    tipo = "estado"
                    mensaje = f"Tu reclamo '{bache.titulo}' cambió a {bache.get_estado_display()}."
                elif cambio_coment:
                    tipo = "comentario"
                    mensaje = f"El municipio dejó un comentario en tu reclamo '{bache.titulo}'."
                else:
                    # teóricamente no entra acá porque hubo_cambio=True,
                    # pero lo dejamos por seguridad
                    tipo = "info"
                    mensaje = f"Hubo una actualización en tu reclamo '{bache.titulo}'."

                Notificacion.objects.create(
                    destinatario=bache.vecino,
                    bache=bache,
                    tipo=tipo,
                    mensaje=mensaje
                )

        return redirect("panel_municipio")

    # GET (tus filtros los podés volver a enchufar acá como ya los tenías)
    baches = (
    Bache.objects
    .annotate(votos_count=Count("upvotes"))
    .order_by("-votos_count", "-fecha_creacion")
    )

    total = baches.count()
    nuevos = baches.filter(estado="nuevo").count()
    en_gestion = baches.filter(estado="en_gestion").count()
    resueltos = baches.filter(estado="resuelto").count()

    return render(request, "baches/panel_municipio.html", {
        "baches": baches,
        "ESTADO_CHOICES": Bache.ESTADO_CHOICES,
        "total": total,
        "nuevos": nuevos,
        "en_gestion": en_gestion,
        "resueltos": resueltos,
    })



# LOGOUT
def logout_view(request):
    logout(request)  # borra la sesión del usuario
    return redirect('lista_baches')  # siempre vuelve al inicio



# REGISTRARSE
def registro(request):
    if request.method == "POST":
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data.get("email", "")
            user.first_name = form.cleaned_data.get("first_name", "")
            user.last_name = form.cleaned_data.get("last_name", "")
            user.save()

            # Creamos perfil vecino
            Perfil.objects.create(
                user=user,
                rol="vecino",
                dni=form.cleaned_data.get("dni", ""),
                fecha_nacimiento=form.cleaned_data.get("fecha_nacimiento"),
                telefono=form.cleaned_data.get("telefono", ""),
                domicilio=form.cleaned_data.get("domicilio", ""),
            )

            # Logueo automático y a la home
            login(request, user)
            return redirect("lista_baches")
    else:
        form = RegistroForm()

    return render(request, "registration/registro.html", {"form": form})



# EXPORTAR A CSV
@login_required
def exportar_baches_csv(request):
    if not hasattr(request.user, 'perfil') or request.user.perfil.rol != 'municipio':
        return HttpResponseForbidden("No tenés permisos.")

    baches = Bache.objects.all().order_by("-fecha_creacion")

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="baches_pozosya.csv"'

    writer = csv.writer(response)
    writer.writerow([
        "ID", "Titulo", "Calle", "Altura", "Barrio", "Severidad",
        "Estado", "Latitud", "Longitud", "Vecino", "Fecha"
    ])

    for b in baches:
        writer.writerow([
            b.id, b.titulo, b.calle, b.altura, b.barrio,
            b.severidad, b.estado, b.latitud, b.longitud,
            b.vecino.username if b.vecino else "",
            b.fecha_creacion.strftime("%d/%m/%Y %H:%M")
        ])

    return response



# DETALLE
def detalle_bache(request, pk):
    bache = get_object_or_404(Bache, pk=pk)

    historial = (
        bache.historial
        .select_related("actor")
        .order_by("-fecha")
    )

    return render(
        request,
        "baches/detalle_bache.html",
        {"bache": bache, "historial": historial}
    )



# NOTIFICACIONES
@login_required
def mis_notificaciones(request):
    # Trae todas las notificaciones del usuario logueado
    notifs = (
        Notificacion.objects.filter(destinatario=request.user).order_by("-fecha")
    )

    # Cantidad no leídas para mostrar en la página también
    no_leidas = notifs.filter(leida=False).count()

    return render(request, "baches/notificaciones.html", {"notificaciones": notifs, "no_leidas": no_leidas})



# MARCAR NOTIFICACIONES COMO LEÍDAS
@login_required
def marcar_notificacion_leida(request, notif_id):
    try:
        notif = Notificacion.objects.get(id=notif_id, destinatario=request.user)
        notif.leida = True
        notif.save()
    except Notificacion.DoesNotExist:
        pass

    # Si querés que al tocarla te lleve al detalle del bache:
    return redirect("detalle_bache", pk=notif.bache.id)



# A DEFINIR
@login_required
def mis_baches(request):
    baches = Bache.objects.filter(vecino=request.user).order_by("-fecha_creacion")

    baches_con_coords = (
        baches
        .exclude(latitud__isnull=True)
        .exclude(longitud__isnull=True)
    )

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

    return render(request, "baches/mis_baches.html", {
        "baches": baches,
        "baches_data": baches_data,
    })



# UPVOTE
@login_required
def toggle_upvote(request, pk):
    bache = get_object_or_404(Bache, pk=pk)

    if request.user in bache.upvotes.all():
        bache.upvotes.remove(request.user)
    else:
        bache.upvotes.add(request.user)

    return redirect("detalle_bache", pk=pk)



# MENSAJE DE ERROR
class CustomLoginView(LoginView):
    template_name = "registration/login.html"

    def form_invalid(self, form):
        messages.error(self.request, "Usuario o contraseña incorrectos.")
        return super().form_invalid(form)