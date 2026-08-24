from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Rutas de la API REST
    path('api/', include('apps.firmas.urls_api')), 
    
    # Rutas de vistas HTML (debe ser path vacío '')
    path('', include('apps.firmas.urls')), 
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)