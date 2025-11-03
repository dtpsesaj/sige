from django.contrib import admin
from .models import (CatEtapas, CatCategoria,CatRespuestaDefault,CatSolicitud,CatContacto,
                    CatEntidad,EntidadSistema,Historico, EtapasSistema, ObservacionEtapa)

class EntidadSistemaAdmin(admin.ModelAdmin):
    list_display = ("get_municipio","entidad", "sistema", "fuente")
    list_display_links = ("entidad", "sistema")
    list_filter = ("entidad", "sistema", "fuente", "operacion_modo")
    search_fields = ("entidad", "sistema", "operacion_modo",)
    ordering = ("activo", "sistema", "fuente",)

    def get_municipio(self, obj):
        if obj.entidad:
            if obj.entidad.municipio:
                return obj.entidad.municipio.nombre
            else:
                return ""
        else: 
            return "Sin municipio"
    get_municipio.short_description = 'Municipio'

class HistoricoAdmin(admin.ModelAdmin):
    list_display = ("tipo_evento", "entidad", "autor", "created_at")
    list_filter = ("tipo_evento", "created_at", "autor", "entidad")
    search_fields = ("tipo_evento", "descripcion", "entidad__nombre", "contacto__nombres", "autor__username")
    ordering = ("-created_at",)

class EtapasSistemasAdmin(admin.ModelAdmin):
    list_display = ("id", "fecha_etapa", "etapa", "get_etapa_order", "get_sistema", "get_entidad")
    list_display_links = ("id",)
    list_filter = ( "descripcion",)
    search_fields = ("descripcion","fecha_etapa",)
    ordering = ("fecha_etapa","descripcion",)

    def get_entidad(self, obj):
        if obj.entidadSistema:
            if obj.entidadSistema.entidad:
                return obj.entidadSistema.entidad.nombre
            else:
                return ""
        else: 
            return "Sin entidad"
    get_entidad.short_description = 'Entidad'

    def get_sistema(self, obj):
        if obj.entidadSistema:
            if obj.entidadSistema.sistema:
                return obj.entidadSistema.sistema
            else:
                return ""
        else: 
            return "Sin entidad"
    get_sistema.short_description = 'Sistema'

    def get_etapa_order(self, obj):
        if obj.etapa:
            if obj.etapa.order:
                return obj.etapa.order
            else:
                return ""
        else: 
            return "Sin entidad"
    get_etapa_order.short_description = 'Orden'


class ObservacionEtapaAdmin(admin.ModelAdmin):
    list_display = ("id", "fecha", "descripcion", "autor", "tipo_interaccion")
    list_display_links = ("id",)
    list_filter = ( "fecha","descripcion", "tipo_interaccion")
    search_fields = ("descripcion","autor", "tipo_interaccion",)
    ordering = ("fecha","autor","tipo_interaccion",)


class CatCategoriaAdmin(admin.ModelAdmin):
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
    list_display = ( "nombre", "region", "activo", "usuario", "contacto_oic")
    list_filter = ("region", "activo", "nombre", "usuario")
    search_fields = ("nombre", "region", "usuario")
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

class CatEtapasAdmin(admin.ModelAdmin):
    list_display = ("id", "sistema", "nombre", "codigo", "order", "get_parent", )
    list_display_links = ("nombre", "id",)
    list_filter = ("sistema", "created_at", "codigo",)
    search_fields = ("nombre","sistema", "codigo",)
    ordering = ("sistema","nombre","codigo",)

    def get_parent(self, obj):
        if not obj.parent:
            return "Parent"
        else: 
            return "Children"
        
    get_parent.short_description = 'Parent'

admin.site.register(CatCategoria, CatCategoriaAdmin)
admin.site.register(CatContacto, CatContactoAdmin)
admin.site.register(CatEntidad, CatEntidadAdmin)
admin.site.register(CatSolicitud, CatSolicitudAdmin)
admin.site.register(CatRespuestaDefault, CatRespuestaDefaultAdmin)
admin.site.register(CatEtapas, CatEtapasAdmin)

admin.site.register(EntidadSistema, EntidadSistemaAdmin)
admin.site.register(Historico, HistoricoAdmin)
admin.site.register(EtapasSistema, EtapasSistemasAdmin)
admin.site.register(ObservacionEtapa, ObservacionEtapaAdmin)