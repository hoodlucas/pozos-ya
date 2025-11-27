from django import forms
from .models import Bache
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Perfil

BARRIOS_LOMAS = [
    ("", "Seleccionar barrio..."),
    ("Banfield", "Banfield"),
    ("Temperley", "Temperley"),
    ("Lomas de Zamora", "Lomas de Zamora"),
    ("Llavallol", "Llavallol"),
    ("Turdera", "Turdera"),
    ("Villa Centenario", "Villa Centenario"),
    ("Ingeniero Budge", "Ingeniero Budge"),
    ("Villa Fiorito", "Villa Fiorito"),
    ("Parque Barón", "Parque Barón"),
    ("Santa Catalina", "Santa Catalina"),
    ("San Jose", "San Jose")
    # si querés agregamos más después
]

class BacheForm(forms.ModelForm):
    barrio = forms.ChoiceField(choices=BARRIOS_LOMAS, required=False)

    class Meta:
        model = Bache
        fields = [
            'titulo', 'descripcion', 'calle', 'altura',
            'barrio', 'severidad', 'latitud', 'longitud', 'imagen',
        ]
        widgets = {
            'latitud': forms.HiddenInput(),
            'longitud': forms.HiddenInput(),
        }




class RegistroForm(UserCreationForm):
    first_name = forms.CharField(label="Nombre", max_length=150, required=True)
    last_name = forms.CharField(label="Apellido", max_length=150, required=True)
    email = forms.EmailField(label="Email", required=False)

    dni = forms.CharField(label="DNI", max_length=15, required=False)
    fecha_nacimiento = forms.DateField(
        label="Fecha de nacimiento",
        required=False,
        widget=forms.DateInput(attrs={"type": "date"})
    )
    telefono = forms.CharField(label="Teléfono", max_length=30, required=False)
    domicilio = forms.CharField(label="Domicilio", max_length=200, required=False)

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
            "dni",
            "fecha_nacimiento",
            "telefono",
            "domicilio",
        ]

