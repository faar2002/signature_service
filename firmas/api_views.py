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


class SolicitarOTPAPIView(APIView):
    """
    POST: Solicita la generación y envío del OTP al microservicio.
    """
    def post(self, request, *args, **kwargs):
        serializer = OTPSolicitarSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        uuid_trans = serializer.validated_data['uuid_transaccion']
        transaccion = get_object_or_404(TransaccionFirma, uuid=uuid_trans)

        # Llamada al microservicio OTP
        respuesta_otp = otp_service.solicitar_codigo(
            email=transaccion.email_firmante, 
            app_source="ServicioFirma"
        )

        # Manejo de error si el servicio OTP retorna un string (ej. 404 correo suspendido)
        if isinstance(respuesta_otp, str):
            mensaje_error = "El servicio de OTP no está disponible."
            if '{"error":' in respuesta_otp:
                try:
                    json_part = respuesta_otp.split(' - ')[1]
                    mensaje_error = json.loads(json_part).get('error', mensaje_error)
                except Exception:
                    mensaje_error = respuesta_otp

            return Response({
                "status": "error",
                "message": mensaje_error
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "status": "success",
            "message": "Código OTP enviado correctamente",
            "data": respuesta_otp
        }, status=status.HTTP_200_OK)


class ValidarOTPAPIView(APIView):
    """
    POST: Valida si el código ingresado coincide con el enviado al correo.
    """
    def post(self, request, *args, **kwargs):
        serializer = OTPValidarSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        uuid_trans = serializer.validated_data['uuid_transaccion']
        codigo = serializer.validated_data['otp_code']
        transaccion = get_object_or_404(TransaccionFirma, uuid=uuid_trans)

        es_valido = otp_service.validar_codigo(
            email=transaccion.email_firmante, 
            codigo=codigo, 
            app_source="ServicioFirma"
        )

        if es_valido:
            # Marcamos en la sesión actual de Django que la transacción fue autenticada
            sesion_key = f"otp_validado_{transaccion.uuid}"
            request.session[sesion_key] = True
            request.session.modified = True

            return Response({
                "status": "success",
                "valid": True,
                "message": "Código OTP validado correctamente."
            }, status=status.HTTP_200_OK)

        return Response({
            "status": "error",
            "valid": False,
            "message": "Código inválido o expirado."
        }, status=status.HTTP_400_BAD_REQUEST)