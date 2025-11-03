from django.urls import path, include,re_path 
from . import views

app_name = 'helpdesk'

urlpatterns = [
    path("", views.mesa_ayuda, name="helpdesk")
]