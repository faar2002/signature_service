import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404

from .models import TransaccionFirma
from .serializers import (
    TransaccionCrearSerializer, 
    OTPSolicitarSerializer, 
    OTPValidarSerializer
)
from .services.otp_service import OTPService

otp_service = OTPService()


class CrearTransaccionAPIView(APIView):
    """
    POST: Crea un nuevo registro de transacción y almacena el PDF original.
    """
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request, *args, **kwargs):
        serializer = TransaccionCrearSerializer(data=request.data)
        if serializer.is_valid():
            transaccion = serializer.save()
            return Response({
                "status": "success",
                "message": "Transacción creada exitosamente",
                "data": serializer.data,
                "url_firma": f"/firmar/{transaccion.uuid}/"
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            "status": "error",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


otp_service = OTPService()

class SolicitarOTPAPIView(APIView):
    def post(self, request, *args, **kwargs):
        uuid_trans = request.data.get('uuid_transaccion')
        transaccion = get_object_or_404(TransaccionFirma, uuid=uuid_trans)

        respuesta_otp = otp_service.solicitar_codigo(
            email=transaccion.email_firmante, 
            nombre_firmante=transaccion.nombre_firmante
        )

        if respuesta_otp.get("status") == "error":
            return Response({
                "status": "error",
                "valid": False,
                "message": respuesta_otp.get("message"),  # <-- "El correo está temporalmente bloqueado por 2 minuto(s) más."
                "retry_after_seconds": respuesta_otp.get("retry_after_seconds")
            }, status=status.HTTP_403_FORBIDDEN if respuesta_otp.get("blocked") else status.HTTP_400_BAD_REQUEST)

        return Response({
            "status": "success",
            "message": "Código OTP enviado correctamente"
        }, status=status.HTTP_200_OK)


class ValidarOTPAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = OTPValidarSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        uuid_trans = serializer.validated_data['uuid_transaccion']
        codigo = serializer.validated_data['otp_code']
        transaccion = get_object_or_404(TransaccionFirma, uuid=uuid_trans)

        # Invocamos la validación en el microservicio OTP
        respuesta_otp = otp_service.validar_codigo(
            email=transaccion.email_firmante, 
            codigo=codigo
        )

        # Si la validación fue exitosa
        if isinstance(respuesta_otp, dict) and respuesta_otp.get("valid"):
            sesion_key = f"otp_validado_{transaccion.uuid}"
            request.session[sesion_key] = True
            request.session.modified = True

            return Response({
                "status": "success",
                "valid": True,
                "message": "Código OTP validado correctamente."
            }, status=status.HTTP_200_OK)

        # SI EL USUARIO O CORREO ESTÁ BLOQUEADO POR REINTENTOS FALLIDOS (HTTP 403 / BLOCKED)
        if isinstance(respuesta_otp, dict) and (respuesta_otp.get("status") == "BLOCKED" or respuesta_otp.get("blocked")):
            return Response({
                "status": "error",
                "valid": False,
                "blocked": True,
                "message": respuesta_otp.get("message") or respuesta_otp.get("error") or "El correo ha sido bloqueado por superar el número de intentos permitidos."
            }, status=status.HTTP_403_FORBIDDEN)

        # Error estándar por código incorrecto
        mensaje_error = respuesta_otp.get("message") if isinstance(respuesta_otp, dict) else "Código OTP inválido o expirado."
        return Response({
            "status": "error",
            "valid": False,
            "blocked": False,
            "message": mensaje_error
        }, status=status.HTTP_400_BAD_REQUEST)