import uuid
from django.db import models
from django.conf import settings

class CatContacto(models.Model):
    class Meta:
        db_table = "cat_contactos"
        verbose_name = "Catálogo Contacto"
        verbose_name_plural = "Catálogo Contactos"
        ordering = ["apellido_paterno", "nombres"]

    TIPO_CHOICES = [
        ("OIC", "OIC"),
        ("Tecnico", "Técnico"),
        ("Sindico", "Síndico"),
        ("PM", "PM"),
        ("Otro", "Otro"),
    ]
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    entidad = models.ForeignKey(
        "CatEntidad",
        on_delete=models.CASCADE,
        related_name="entidad"
    )

    nombres = models.CharField(max_length=150, db_index=True)
    apellido_paterno = models.CharField(max_length=150)
    apellido_materno = models.CharField(max_length=150, blank=True, null=True)
    fecha_inicio = models.DateField(blank=True, null=True)
    fecha_fin = models.DateField(blank=True, null=True)
    telefono_oficina = models.CharField(max_length=50, blank=True, null=True)
    telefono_personal = models.CharField(max_length=50, blank=True, null=True)
    correo = models.EmailField(max_length=255, blank=True, null=True, db_index=True)
    puesto = models.CharField(max_length=150, blank=True, null=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default="Otro")
    otro = models.CharField(max_length=100, blank=True, null=True)
    activo = models.BooleanField(default=True, db_index=True)

    def __str__(self):
        return f"{self.nombres} {self.apellido_paterno} ({self.tipo})"


class CatEntidad(models.Model):
    class Meta:
        db_table = "cat_entidades"
        verbose_name = "Catálogo Entidad"
        verbose_name_plural = "Catálogo Entidades"
        ordering = ["nombre"]

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    numero_municipio = models.CharField(max_length=10, blank=True, null=True)
    nombre = models.CharField(max_length=255)
    region = models.CharField(max_length=100, blank=True, null=True)
    personalidad = models.CharField(max_length=100, blank=True, null=True)
    patrimonio = models.CharField(max_length=255, blank=True, null=True)
    base_legal = models.CharField(max_length=255, blank=True, null=True)
    ambito_gobierno = models.CharField(max_length=100, blank=True, null=True)
    poder = models.CharField(max_length=100, blank=True, null=True)
    clasificacion = models.CharField(max_length=100, blank=True, null=True)
    servidores_publicos = models.IntegerField(default=0)
    control_tribunal = models.CharField(max_length=150, blank=True, null=True)
    activo = models.BooleanField(default=True)

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="usuario",
    )
    contacto_oic = models.ForeignKey(
        "CatContacto",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="contacto_oic",
    )
    contacto_tecnico = models.ForeignKey(
        "CatContacto",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="contacto_tecnico",
    )


    def __str__(self):
        return self.nombre


class CatCategoria(models.Model):
    class Meta:
        db_table = "cat_categorias"
        verbose_name = "Catálogo Categoría"
        verbose_name_plural = "Catálogo Categorías"
        ordering = ["titulo"]

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    titulo = models.CharField(max_length=200)
    visible = models.BooleanField(default=True)

    def __str__(self):
        return self.titulo


class CatRespuestaDefault(models.Model):
    class Meta:
        db_table = "cat_respuestas_default"
        verbose_name = "Catálogo Respuesta default"
        verbose_name_plural = "Catálogo Respuestas default"
        ordering = ["titulo"]

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    titulo = models.CharField(max_length=255)
    respuesta = models.TextField()
    visible = models.BooleanField(default=True)

    def __str__(self):
        return self.titulo

class CatSolicitud(models.Model):
    class Meta:
        db_table = "cat_solicitudes"
        verbose_name = "Catálogo Solicitud"
        verbose_name_plural = "Catálogo Solicitudes"
        ordering = ["-created_at"]

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    fecha_solicitud = models.DateField(blank=True, null=True)

    entidad_sistema = models.ForeignKey(
        "EntidadSistema",
        on_delete=models.CASCADE,
        related_name="entidad_sistema"
    )
    folio = models.CharField(max_length=100, unique=True, blank=True, null=True)
    tipo_solicitud = models.CharField(max_length=150, blank=True, null=True)
    quien_recibe_ost = models.CharField(max_length=255, blank=True, null=True)

    quien_recibe_dtp = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="quien_recibe_dtp",
    )

    impreso = models.BooleanField(default=False)

    def __str__(self):
        return f"Solicitud {self.folio} - {self.entidad_sistema}"

class EntidadSistema(models.Model):
    class Meta:
        db_table = "sige_entidades_sistema"
        verbose_name = "Entidad Sistema"
        verbose_name_plural = "Entidades Sistema"
        ordering = ["-created_at"]

    FUENTE_CHOICES = [
        ("SESAJ", "SESAJ"),
        ("SEPIFAPE", "SEPIFAPE"),
        ("Propio", "Propio"),
    ]
    MODO_CHOICES = [
        ("online", "Online"),
        ("local", "Local"),
        ("multiente", "Multiente"),
    ]
    SISTEMA_CHOICES = [
        ("S1", "S1"),
        ("S2", "S2"),
        ("S3", "S3"),
        ("S4", "S4"),
        ("S5", "S5"),
        ("S6", "S6"),
    ]

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sistema = models.CharField(max_length=5, choices=SISTEMA_CHOICES, blank=True, null=True)
    licencia = models.CharField(max_length=555, blank=True, null=True)

    entidad = models.ForeignKey(
        CatEntidad,
        on_delete=models.CASCADE,
        related_name="entidad_relacion"
    )

    fuente = models.CharField(max_length=20, choices=FUENTE_CHOICES, blank=True, null=True)
    operacion_modo = models.CharField(max_length=20, choices=MODO_CHOICES, blank=True, null=True)
    operacion_fecha = models.DateField(blank=True, null=True)
    sistema_operativo = models.CharField(max_length=255, blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    api_auth = models.CharField(max_length=255, blank=True, null=True)
    api_declaraciones = models.CharField(max_length=255, blank=True, null=True)
    api_username = models.CharField(max_length=255, blank=True, null=True)
    api_password = models.CharField(max_length=255, blank=True, null=True)
    api_clien_id = models.CharField(max_length=255, blank=True, null=True)
    api_client_secret = models.CharField(max_length=255, blank=True, null=True)
    api_scope = models.CharField(max_length=255, blank=True, null=True)
    api_grant_type = models.CharField(max_length=255, blank=True, null=True)
    cantidad_declaraciones = models.IntegerField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.entidad} - {self.sistema} ({self.fuente})"




class Historico(models.Model):
    class Meta:
        db_table = "sige_historico"
        verbose_name = "Histórico"
        verbose_name_plural = "Históricos"
        ordering = ["-created_at"]

    EVENTO_CHOICES = [
        ("cambio_datos","Cambio de datos"),
        ("llamada_informativa","Llamada informativa"),
        ("llamada_tarea","Llamada con tarea pendiente"),
        ("ticket_creado","Ticket creado"),
        ("ticket_actualizado","Ticket actualizado"),
        ("pdn","Seguimeinto conexión PDN")
    ]

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tipo_evento = models.CharField(max_length=50, choices=EVENTO_CHOICES)
    descripcion = models.TextField()
    datos_anteriores = models.JSONField(blank=True, null=True)
    datos_nuevos = models.JSONField(blank=True, null=True)

    entidad = models.ForeignKey(
        CatEntidad,
        on_delete=models.CASCADE,
        related_name="entidad_historicos"
    )
    contacto = models.ForeignKey(
        CatContacto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="historico_contacto"
    )
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="historicos_autor"
    )


    def __str__(self):
        return f"Histórico {self.tipo_evento} - {self.entidad}"
