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

    def __str__(self):
        return f"{self.id_documento_externo} - {self.nombre_firmante}"
