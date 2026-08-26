import uuid
from django.db import models

class TransaccionFirma(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    nombre_firmante = models.CharField(max_length=255)
    email_firmante = models.EmailField()
    id_documento_externo = models.CharField(max_length=100)
    pdf_original = models.FileField(upload_to='docs/originales/')
    pdf_firmado = models.FileField(upload_to='docs/firmados/', blank=True, null=True)
    estado = models.CharField(max_length=20, default='PENDIENTE') # PENDIENTE, FIRMADO
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    pagina_firma = models.IntegerField(default=1, verbose_name="Página de Firma")
    pos_x = models.FloatField(default=100.0, verbose_name="Coordenada X (puntos PDF)")
    pos_y = models.FloatField(default=100.0, verbose_name="Coordenada Y (puntos PDF)")

    def __str__(self):
        return f"{self.id_documento_externo} - {self.nombre_firmante}"

class AplicacionAutorizada(models.Model):
    nombre_app = models.CharField(max_length=100, verbose_name="Nombre de la Aplicación")
    system_name = models.SlugField(max_length=50, unique=True, verbose_name="Código del Sistema")
    system_token = models.CharField(max_length=128, unique=True, default=uuid.uuid4, verbose_name="System Token (X-System-Token)")
    ip_permitidas = models.TextField(blank=True, null=True, help_text="IPs permitidas separadas por comas. Dejar en blanco para permitir cualquier IP.")
    is_active = models.BooleanField(default=True, verbose_name="¿Activa?")
    rate_limit = models.IntegerField(default=60, help_text="Límite de peticiones por minuto.")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")

    class Meta:
        verbose_name = "Aplicación Autorizada"
        verbose_name_plural = "Aplicaciones Autorizadas"
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.nombre_app} ({self.system_name})"
