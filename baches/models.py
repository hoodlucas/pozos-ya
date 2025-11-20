from django.db import models
from django.contrib.auth.models import User


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

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.titulo} - {self.calle} {self.altura}"




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

