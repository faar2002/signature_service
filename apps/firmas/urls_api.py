from django.urls import path
from .api_views import (
    CrearTransaccionAPIView, 
    SolicitarOTPAPIView, 
    ValidarOTPAPIView
)

urlpatterns = [
    path('v1/transacciones/crear/', CrearTransaccionAPIView.as_view(), name='api_crear_transaccion'),
    path('v1/otp/solicitar/', SolicitarOTPAPIView.as_view(), name='api_solicitar_otp'),
    path('v1/otp/validar/', ValidarOTPAPIView.as_view(), name='api_validar_otp'),
]