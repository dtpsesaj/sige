from django.urls import path, include   
from . import views

from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'catalogos/categoria', views.CatCategoriaViewSet)
router.register(r'catalogos/respuesta_default', views.CatRespuestaDefaultViewSet)
router.register(r'catalogos/solicitud', views.CatSolicitudViewSet)
router.register(r'catalogos/contacto', views.CatContactoViewSet)
router.register(r'catalogos/entidad', views.CatEntidadViewSet)

app_name = 'sitio'

urlpatterns = [
    path('', views.home, name='home'),
    path('sitio/', include(router.urls)),
]
