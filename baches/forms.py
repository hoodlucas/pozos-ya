from django import forms
from .models import Bache

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
    # si querés agregamos más después
]

class BacheForm(forms.ModelForm):
    barrio = forms.ChoiceField(choices=BARRIOS_LOMAS, required=False)

    class Meta:
        model = Bache
        fields = [
            'titulo', 'descripcion', 'calle', 'altura',
            'barrio', 'severidad', 'latitud', 'longitud'
        ]
        widgets = {
            'latitud': forms.HiddenInput(),
            'longitud': forms.HiddenInput(),
        }
