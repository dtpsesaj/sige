import uuid
from django.db import models
from django.conf import settings
from sitio.models import CatEntidad, CatCategoria

class Ticket(models.Model):
    class Meta:
        db_table = "helpdesk_tickets"
        verbose_name = "Ticket"
        verbose_name_plural = "Tickets"
        ordering = ["-created_at"]

    ESTADO_CHOICES = [
        ("Abierto", "Abierto"),
        ("En Proceso", "En Proceso"),
        ("Cerrado", "Cerrado"),
    ]
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    titulo = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    sistema = models.IntegerField()  # según tu diagrama aparece como int
    prioridad = models.CharField(max_length=50, blank=True, null=True)
    estado = models.CharField(max_length=50, choices=ESTADO_CHOICES, default="Abierto")

    entidad = models.ForeignKey(
        CatEntidad,
        on_delete=models.CASCADE,
        related_name="entidad_ticket"
    )
    categoria = models.ForeignKey(
        CatCategoria,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="categoria"
    )
    asignado_a = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="asignado_a"
    )

    def __str__(self):
        return f"[{self.estado}] {self.titulo} ({self.entidad})"


class TicketsSeguimiento(models.Model):
    class Meta:
        db_table = "helpdesk_tickets_seguimiento"
        verbose_name = "Seguimiento de ticket"
        verbose_name_plural = "Seguimientos de tickets"
        ordering = ["-created_at"]

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    ticket = models.ForeignKey(
        Ticket,   # ajusta al nombre real de tu modelo de tickets
        on_delete=models.CASCADE,
        related_name="tickets"
    )

    entidad = models.ForeignKey(
        CatEntidad,
        on_delete=models.CASCADE,
        related_name="seguimiento_entidad"
    )

    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="seguimiento_autor"
    )

    mensaje = models.TextField()
    publico = models.BooleanField(default=True)
    nuevo_estado = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Seguimiento #{self.id} de Ticket {self.ticket_id}"

