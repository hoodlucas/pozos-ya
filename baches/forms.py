from django import forms
from .models import Bache
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Perfil
from django.contrib.auth.forms import AuthenticationForm

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



class CustomAuthForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Usuario'
        self.fields['password'].label = 'Contraseña'

class RegistroForm(UserCreationForm):
    first_name = forms.CharField(label="Nombre", max_length=150, required=True)
    last_name = forms.CharField(label="Apellido", max_length=150, required=True)
    email = forms.EmailField(label="Email", required=True)  # <- ahora obligatorio
    dni = forms.CharField(label="DNI", max_length=15, required=False)
    fecha_nacimiento = forms.DateField(
        label="Fecha de nacimiento",
        required=False,
        widget=forms.DateInput(attrs={"type": "date"})
    )
    telefono = forms.CharField(label="Teléfono", max_length=30, required=False)
    domicilio = forms.CharField(label="Domicilio", max_length=200, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["username"].label = "Usuario"
        self.fields["password1"].label = "Contraseña"
        self.fields["password2"].label = "Confirmación de contraseña"
        self.fields["username"].help_text = None
        self.fields["password1"].help_text = None
        self.fields["password2"].help_text = None

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

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        # clave para verificación por email:
        user.is_active = False
        if commit:
            user.save()
            # guardo extras en Perfil (ajustá nombres de campos según tu modelo Perfil real)
            Perfil.objects.update_or_create(
                user=user,
                defaults={
                    "dni": self.cleaned_data.get("dni", ""),
                    "fecha_nacimiento": self.cleaned_data.get("fecha_nacimiento"),
                    "telefono": self.cleaned_data.get("telefono", ""),
                    "domicilio": self.cleaned_data.get("domicilio", ""),
                    "rol": "vecino",  # si aplica
                }
            )
        return user



# RECUPERAR CONTRASEÑA
class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(label="Email", required=True)

class PasswordResetConfirmForm(forms.Form):
    code = forms.CharField(label="Código", max_length=6, required=True)
    password1 = forms.CharField(label="Nueva contraseña", widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(label="Repetir contraseña", widget=forms.PasswordInput, required=True)

    def clean(self):
        cleaned = super().clean()
        p1, p2 = cleaned.get("password1"), cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return cleaned