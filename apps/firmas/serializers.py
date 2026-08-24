from rest_framework import serializers
from .models import TransaccionFirma


class TransaccionCrearSerializer(serializers.ModelSerializer):
    """
    Serializador para recibir y validar la creación de una nueva solicitud de firma.
    """
    class Meta:
        model = TransaccionFirma
        fields = [
            'uuid',
            'nombre_firmante',
            'email_firmante',
            'id_documento_externo',
            'pdf_original',
            'estado',
            'fecha_creacion'
        ]
        read_only_fields = ['uuid', 'estado', 'fecha_creacion']

    def validate_email_firmante(self, value):
        """Validación de formato básico de email"""
        return value.lower().strip()


class OTPSolicitarSerializer(serializers.Serializer):
    """
    Validador para requerir el reenvío o solicitud de OTP.
    """
    uuid_transaccion = serializers.UUIDField(required=True)


class OTPValidarSerializer(serializers.Serializer):
    """
    Validador para la verificación del código OTP de 6 dígitos.
    """
    uuid_transaccion = serializers.UUIDField(required=True)
    otp_code = serializers.CharField(max_length=10, min_length=4, required=True)