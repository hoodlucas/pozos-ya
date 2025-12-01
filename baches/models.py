from django.db import models
from django.contrib.auth.models import User

from django.utils import timezone
from datetime import timedelta
import random

# Create your models here.

# POZO
class Bache(models.Model):
    SEVERIDAD_CHOICES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
    ]

    ESTADO_CHOICES = [
        ('nuevo', 'Nuevo'),
        ('en_gestion', 'En gestión'),
        ('resuelto', 'Resuelto'),
    ]
    
    vecino = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    calle = models.CharField(max_length=150)
    altura = models.CharField(max_length=20, blank=True)
    barrio = models.CharField(max_length=100, blank=True)
    severidad = models.CharField(max_length=10, choices=SEVERIDAD_CHOICES, default='media')
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='nuevo')
    latitud = models.FloatField(null=True, blank=True)
    longitud = models.FloatField(null=True, blank=True)
    imagen = models.ImageField(upload_to="baches/", null=True, blank=True)
    upvotes = models.ManyToManyField(User, related_name="baches_votados", blank=True)
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    fecha_resolucion = models.DateTimeField(null=True, blank=True)

    comentario_municipio = models.TextField(blank=True)
    def __str__(self):
        return f"{self.titulo} - {self.calle} {self.altura}"



# HISTORIAL DE CADA POZO
class HistorialBache(models.Model):
    bache = models.ForeignKey("Bache", on_delete=models.CASCADE, related_name="historial")
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    estado_anterior = models.CharField(max_length=15, blank=True)
    estado_nuevo = models.CharField(max_length=15, blank=True)

    comentario_anterior = models.TextField(blank=True)
    comentario_nuevo = models.TextField(blank=True)

    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cambio en bache #{self.bache.id} - {self.fecha:%d/%m/%Y %H:%M}"



# NOTIFICACIÓN
class Notificacion(models.Model):
    TIPOS = [
        ("estado", "Cambio de estado"),
        ("comentario", "Comentario del municipio"),
        ("mixto", "Estado y comentario"),
    ]

    destinatario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notificaciones")
    bache = models.ForeignKey("Bache", on_delete=models.CASCADE, related_name="notificaciones")

    tipo = models.CharField(max_length=20, choices=TIPOS, default="estado")
    mensaje = models.CharField(max_length=255)

    leida = models.BooleanField(default=False)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notif a {self.destinatario.username} - {self.tipo}"



# PERFIL
class Perfil(models.Model):
    ROLES = [
        ('vecino', 'Vecino'),
        ('municipio', 'Municipio'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rol = models.CharField(max_length=20, choices=ROLES, default='vecino')

    dni = models.CharField(max_length=15, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    telefono = models.CharField(max_length=30, blank=True)
    domicilio = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_rol_display()}"



# CÓDIGO DE MAIL
class CodigoEmail(models.Model):
    TIPO_CHOICES = [
        ("verify", "Verificación"),
        ("reset", "Recuperación"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="codigos_email")
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    codigo = models.CharField(max_length=6)
    expira_en = models.DateTimeField()
    usado = models.BooleanField(default=False)
    creado_en = models.DateTimeField(auto_now_add=True)

    def esta_vigente(self):
        return (not self.usado) and timezone.now() < self.expira_en



class CodigoVerificacionEmail(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="codigos_verificacion")
    code_hash = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)

    def is_expired(self):
        return timezone.now() > self.expires_at

    def is_used(self):
        return self.used_at is not None

    def __str__(self):
        return f"Verificación {self.user.username} - expira {self.expires_at:%d/%m/%Y %H:%M}"



class PasswordResetCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reset_codes")
    code_hash = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)

    def is_expired(self):
        return timezone.now() > self.expires_at

    def is_used(self):
        return self.used_at is not None