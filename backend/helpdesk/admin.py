from django.contrib import admin
from .models import Ticket, TicketsSeguimiento
from sitio.models import CatEntidad, CatCategoria

class TicketAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "titulo",
        "estado",
        "entidad",
        "categoria",
        "asignado_a",
        "created_at",
        "updated_at",
    )
    list_display_links = ("id", "titulo")
    list_filter = (
        "estado",
        "prioridad",
        "entidad",
        "categoria",
        "asignado_a",
        "created_at",
    )
    search_fields = (
        "titulo",
        "descripcion",
        "entidad__nombre",
        "categoria__titulo",
        "asignado_a__username",
    )
    ordering = ("-created_at",)

class TicketsSeguimientoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "ticket",
        "entidad",
        "autor",
        "nuevo_estado",
        "publico",
        "created_at",
        "updated_at",
    )
    list_display_links = ("id", "ticket")
    list_filter = (
        "publico",
        "entidad",
        "autor",
        "nuevo_estado",
        "created_at",
    )
    search_fields = (
        "ticket__titulo",
        "mensaje",
        "autor__username",
        "entidad__nombre",
    )
    ordering = ("-created_at",)

admin.site.register(Ticket, TicketAdmin)
admin.site.register(TicketsSeguimiento, TicketsSeguimientoAdmin)