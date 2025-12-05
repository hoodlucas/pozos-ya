"""
URL configuration for pozosya project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from baches import views as baches_views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from baches.views import CustomLoginView
from baches.forms import CustomAuthForm # ¡IMPORTA TU NUEVO FORMULARIO!

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', baches_views.lista_baches, name='lista_baches'), # Principal
    path('nuevo/', baches_views.crear_bache, name='crear_bache'),
    path('municipio/', baches_views.panel_municipio, name='panel_municipio'),
    path("bache/<int:pk>/", baches_views.detalle_bache, name="detalle_bache"),
    path("mis-reclamos/", baches_views.mis_baches, name="mis_baches"),
    path("municipio/export/csv/", baches_views.exportar_baches_csv, name="exportar_baches_csv"),
    path("bache/<int:pk>/upvote/", baches_views.toggle_upvote, name="toggle_upvote"),
    path("verificar/", baches_views.verificar_email, name="verificar_email"),
    
    path("exportar/csv/", baches_views.exportar_baches_csv, name="exportar_baches_csv"),
    path("exportar/excel/", baches_views.exportar_baches_excel, name="exportar_baches_excel"),
    path("exportar/pdf/", baches_views.exportar_baches_pdf, name="exportar_baches_pdf"),
        
    path("recuperar/", baches_views.password_reset_request, name="password_reset_request"),
    path("recuperar/confirmar/", baches_views.password_reset_confirm, name="password_reset_confirm"),
    
    # LOGIN / LOGOUT / REGISTRO
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html', authentication_form=CustomAuthForm), name='login'),
    path('logout/', baches_views.logout_view, name='logout'),
    path("registro/", baches_views.registro, name="registro"),
    
    # NOTIFICACIONES
    path("notificaciones/", baches_views.mis_notificaciones, name="mis_notificaciones"),
    path("notificaciones/<int:notif_id>/leida/", baches_views.marcar_notificacion_leida, name="marcar_notificacion_leida"),
    
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)