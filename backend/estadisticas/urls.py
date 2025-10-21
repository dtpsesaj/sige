from django.urls import path
from . import views

app_name = "estadisticas"

urlpatterns = [
    path('', views.dashboard_estadisticas, name='dashboard'),
    # APIs
    path('api/entidades_por_sistema/', views.EntidadesPorSistemaAPI.as_view(), name='api_entidades_por_sistema'),
    path('api/entidades_conectadas_por_anio/', views.EntidadesConectadasPorAnioAPI.as_view(), name='api_entidades_por_anio'),
    path('api/sistemas_por_region/', views.SistemasPorRegionAPI.as_view(), name='api_sistemas_por_region'),
    path('api/versiones_s1/', views.VersionesSistema1API.as_view(), name='api_versiones_s1'),
    
]
