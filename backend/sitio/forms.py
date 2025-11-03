from django import forms
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.forms import  TextInput,Textarea
from sitio.models import (CatContacto, CatEntidad, CatSolicitud, CatMunicipios, EntidadSistema, EtapasSistema, 
                        Historico, ObservacionEtapa)

import datetime

TRUE_FALSE_CHOICES = (
        (None,'--------'),
        (1, 'Activo'),
        (0, 'Inactivo')
    )
User = get_user_model()

class EntidadForm(forms.ModelForm):
    nombre = forms.CharField(max_length=200, required=False, label="")
    region = forms.CharField(max_length=15, required=False, label="")
    ambito_gobierno = forms.CharField(max_length=50, required=False, label="")
    municipio = forms.ModelChoiceField(
        queryset=CatMunicipios.objects.filter(cat_entidades_federativas=14),
        required=False, 
        label="",
        widget=forms.Select(attrs={'class': 'select2-municipio'}),
    )
    personalidad = forms.CharField(max_length=15,label="", required=False)
    patrimonio = forms.CharField(max_length=15,label="", required=False)
    poder = forms.CharField(max_length=15,label="", required=False)
    base_legal = forms.CharField(
        label="", 
        required=False,
        widget=forms.Textarea(attrs={'rows': 10, 'cols': 60})
    )
    clasificacion = forms.CharField(max_length=15,label="", required=False)
    control_tribunal = forms.CharField(max_length=15,label="", required=False)
    usuario = fusuario = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        label=""
    )

    def __init__(self, *args, **kwargs):
        super(EntidadForm, self).__init__(*args, **kwargs)
        self.fields['contacto_oic'].widget.attrs['readonly'] = True

    class Meta:
        model = CatEntidad
        fields = '__all__'
        #exclude = ['contacto_oic', 'contacto_tecnico', 'usuario']