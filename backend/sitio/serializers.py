from rest_framework import serializers
from .models import CatCategoria,CatRespuestaDefault,CatSolicitud,CatContacto,CatEntidad,EntidadSistema,Historico

class CatCategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CatCategoria
        fields = '__all__'
        extra_kwargs = {
            'titulo': {'required': True},
            'visible': {'required': False},
        }

class CatRespuestaDefaultSerializer(serializers.ModelSerializer):
    class Meta:
        model = CatRespuestaDefault
        fields = '__all__'

class CatSolicitudSerializer(serializers.ModelSerializer):
    class Meta:
        model = CatSolicitud
        fields = '__all__'

class CatContactoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CatContacto
        fields = '__all__'

class CatEntidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = CatEntidad
        fields = '__all__'

