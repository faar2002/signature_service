from django.urls import path
from . import views

urlpatterns = [
    path('firmar//', views.proceso_firma_view, name='proceso_firma'),
    path('exito//', views.exito_view, name='pagina_exito'),
]