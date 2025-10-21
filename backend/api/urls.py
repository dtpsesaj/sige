from django.urls import path, include   
from . import views


app_name = 'api'

urlpatterns = [
    path('', views.api_entidades, name='home'),
    path("catalogo/entidades", views.api_entidades, name="entidades_busqueda"),    
    path("catalogo/entidades/<int:pk>/detalle/", views.entidad_vista_rapida, name="entidad_vista_rapida"),   
    path("catalogo/entidades/sistema/<int:pk>/etapas/", views.obtencion_etapas_por_sistema_entidad, name="entidad_sistema_etapas"),   
]
