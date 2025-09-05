from django.contrib import admin
from .models import CatCategoria,CatRespuestaDefault,CatSolicitud,CatContacto,CatEntidad,EntidadSistema,Historico

class EntidadSistemaAdmin(admin.ModelAdmin):
    list_display = ("entidad", "sistema", "fuente", "operacion_modo", "activo", "created_at")
    list_display_links = ("entidad", "sistema")
    list_filter = ("entidad", "sistema", "fuente", "operacion_modo")
    search_fields = ("entidad", "sistema", "operacion_modo",)
    ordering = ("activo", "sistema", "fuente",)

class HistoricoAdmin(admin.ModelAdmin):
    list_display = ("tipo_evento", "entidad", "autor", "created_at")
    list_filter = ("tipo_evento", "created_at", "autor", "entidad")
    search_fields = ("tipo_evento", "descripcion", "entidad__nombre", "contacto__nombres", "autor__username")
    ordering = ("-created_at",)

class CatCategoriaAdmin(admin.ModelAdmin):
    #Model config
    list_display = ("id", "titulo", "visible", "created_at", "updated_at")
    list_display_links = ("id", "titulo")
    list_filter = ("visible", "created_at")
    search_fields = ("titulo",)
    ordering = ("titulo",)

class CatContactoAdmin(admin.ModelAdmin):
    list_display = ("nombres", "apellido_paterno", "tipo", "entidad", "correo", "activo")
    list_filter = ("tipo", "activo", "entidad", "nombres")
    search_fields = ("nombres", "apellido_paterno", "apellido_materno", "correo", "entidad__nombre")
    ordering = ("apellido_paterno", "nombres")

class CatEntidadAdmin(admin.ModelAdmin):
    list_display = ( "numero_municipio", "nombre", "region", "activo", "usuario", "contacto_oic")
    list_filter = ("region", "activo", "nombre", "usuario")
    search_fields = ("nombre", "numero_municipio", "region", "usuario")
    ordering = ("nombre",)

class CatRespuestaDefaultAdmin(admin.ModelAdmin):
    list_display = ("id", "titulo", "visible", "created_at", "updated_at")
    list_display_links = ("id", "titulo")
    list_filter = ("visible", "created_at")
    search_fields = ("titulo", "respuesta")
    ordering = ("titulo",)

class CatSolicitudAdmin(admin.ModelAdmin):
    list_display = ( "folio", "tipo_solicitud", "entidad_sistema", "quien_recibe_dtp", "impreso", "created_at")
    list_filter = ("tipo_solicitud", "impreso", "created_at")
    search_fields = ("folio", "tipo_solicitud", "entidad_sistema__entidad__nombre", "quien_recibe_dtp__username")
    ordering = ("-created_at",)

admin.site.register(CatCategoria, CatCategoriaAdmin)
admin.site.register(CatContacto, CatContactoAdmin)
admin.site.register(CatEntidad, CatEntidadAdmin)
admin.site.register(CatSolicitud, CatSolicitudAdmin)
admin.site.register(CatRespuestaDefault, CatRespuestaDefaultAdmin)

admin.site.register(EntidadSistema, EntidadSistemaAdmin)
admin.site.register(Historico, HistoricoAdmin)