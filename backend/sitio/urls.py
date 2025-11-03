from django.urls import path, include,re_path 
from . import views

from rest_framework.routers import DefaultRouter
from django.contrib.auth import views as auth_views


router = DefaultRouter()
router.register(r'catalogos/categoria', views.CatCategoriaViewSet)
router.register(r'catalogos/respuesta_default', views.CatRespuestaDefaultViewSet)
router.register(r'catalogos/solicitud', views.CatSolicitudViewSet)
router.register(r'catalogos/contacto', views.CatContactoViewSet)
router.register(r'catalogos/entidad', views.CatEntidadViewSet)

app_name = 'sitio'


urlpatterns = [
        path('', views.login_view, name='login'),
        path('logout/', views.logout_view, name='logout'),
        path("recuperar-password/", views.password_reset_request, name="password_reset_request"),
        path("password-reset/",
                auth_views.PasswordResetView.as_view(
                template_name="mails/password_reset_form.html",
                email_template_name="mails/password_reset_email.html",
                subject_template_name="mails/password_reset_subject.txt",
                success_url="/password-reset/enviado/",
                ),
                name="password_reset",
        ),
        path("password-reset/enviado/",
                auth_views.PasswordResetDoneView.as_view(
                template_name="mails/password_reset_done.html"
                ),
                name="password_reset_done",
        ),
        path("password-reset/<uidb64>/<token>/",
                auth_views.PasswordResetConfirmView.as_view(
                template_name="mails/password_reset_confirm.html",
                success_url="/password-reset/completado/",
                ),
                name="password_reset_confirm",
        ),
        path("password-reset/completado/",
                auth_views.PasswordResetCompleteView.as_view(
                template_name="mails/password_reset_complete.html"
                ),
                name="password_reset_complete",
        ),
        path('restframework/', include(router.urls)),
        path("entidades/", views.modulo_entidades, name="entidades"),
        path('entidades/nueva/', views.EntidadCreateView.as_view(), name='entidad-crear'),
        path("estadisticas/", views.modulo_estadisticas, name="estadisticas"),
        path('catalogo/entidad/nuevo/', views.EntidadView.as_view(), 
                name='entidad-nueva'),
        re_path(r'^catalogo/entidad/(?P<id>\d+)/detalles/$',views.EntidadView.as_view(),
                name='entidad-detalle'),
        re_path(r'^catalogo/entidad/(?P<id>\d+)/actualizar/$',views.EntidadView.as_view(),
                name='entidad-actualizar'),
        re_path(r'^catalogo/entidad/(?P<entidad_id>\d+)/contacto/agregar/$', views.agregar_contacto_ajax, 
                name='agregar_contacto_ajax'),
        path("catalogo/entidad/<int:entidad_id>/contacto/<int:contacto_id>/actualizar/", views.actualizar_contacto_ajax,
                name="actualizar_contacto_ajax"),
        re_path(r'^catalogo/entidad/(?P<id>(\d+|nuevo))/nuevo/guardar$', views.EntidadView.as_view(), 
                name='entidad-nueva-guardar'),
        #path("api/catalogo/entidades", views.api_entidades, name="entidades_busqueda"),    
        #path("api/catalogo/entidades/<int:pk>/detalle/", views.entidad_vista_rapida, name="entidad_vista_rapida"),   
]
