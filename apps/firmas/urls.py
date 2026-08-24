from django.urls import path
from . import views

urlpatterns = [
    # Path vacío para cargar el dashboard directamente al entrar a http://127.0.0.1:8000/
    path('', views.solicitar_firma_view, name='solicitar_firma'),
    
    # Sin la barra inicial en 'firmar/' ni en 'exito/'
    path('firmar/<uuid:uuid_firma>/', views.firmar_view, name='firmar'),
    path('exito/<uuid:uuid_firma>/', views.exito_view, name='exito'),
]