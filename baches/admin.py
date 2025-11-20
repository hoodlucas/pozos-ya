from django.contrib import admin
from .models import Bache, Perfil

# Register your models here.

@admin.register(Bache)
class BacheAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'calle', 'barrio', 'severidad', 'estado', 'fecha_creacion')
    list_filter = ('barrio', 'severidad', 'estado')
    search_fields = ('titulo', 'calle', 'barrio')


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('user', 'rol', 'dni', 'telefono')
    list_filter = ('rol',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'dni')


