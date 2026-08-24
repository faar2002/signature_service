from django.contrib import admin
from django.utils.html import format_html
from .models import AplicacionAutorizada, TransaccionFirma

@admin.register(AplicacionAutorizada)
class AplicacionAutorizadaAdmin(admin.ModelAdmin):
    list_display = ('nombre_app', 'system_name', 'system_token', 'is_active', 'rate_limit', 'fecha_creacion')
    list_filter = ('is_active', 'fecha_creacion')
    search_fields = ('nombre_app', 'system_name', 'system_token')
    readonly_fields = ('fecha_creacion',)


@admin.register(TransaccionFirma)
class TransaccionFirmaAdmin(admin.ModelAdmin):
    # Campos que se muestran en la lista principal del Admin
    list_display = (
        'id_documento_externo',
        'nombre_firmante',
        'email_firmante',
        'estado_badge',
        'fecha_creacion',
        'descargar_pdf_firmado'
    )

    # Filtros laterales
    list_filter = ('estado', 'fecha_creacion')

    # Buscador por texto
    search_fields = (
        'nombre_firmante', 
        'email_firmante', 
        'id_documento_externo', 
        'uuid'
    )

    # Campos de solo lectura para evitar modificaciones accidentales
    readonly_fields = ('uuid', 'fecha_creacion', 'descargar_pdf_original', 'descargar_pdf_firmado')

    # Organización del formulario detallado
    fieldsets = (
        ('Información de la Transacción', {
            'fields': ('uuid', 'id_documento_externo', 'estado', 'fecha_creacion')
        }),
        ('Datos del Firmante', {
            'fields': ('nombre_firmante', 'email_firmante')
        }),
        ('Archivos PDF', {
            'fields': ('pdf_original', 'descargar_pdf_original', 'pdf_firmado', 'descargar_pdf_firmado')
        }),
    )

    # Método para mostrar un badge de color según el estado
    @admin.display(description='Estado')
    def estado_badge(self, obj):
        if obj.estado == 'FIRMADO':
            color = '#16a34a' # Verde
        elif obj.estado == 'PENDIENTE':
            color = '#d97706' # Naranja/Amarillo
        else:
            color = '#dc2626' # Rojo
            
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 12px; font-weight: bold; font-size: 0.75rem;">{}</span>',
            color,
            obj.estado
        )

    # Enlace rápido para descargar el PDF original
    @admin.display(description='PDF Original')
    def descargar_pdf_original(self, obj):
        if obj.pdf_original:
            return format_html('<a href="{}" target="_blank">📄 Ver Original</a>', obj.pdf_original.url)
        return "No adjunto"

    # Enlace rápido para descargar el PDF firmado
    @admin.display(description='PDF Firmado')
    def descargar_pdf_firmado(self, obj):
        if obj.pdf_firmado:
            return format_html('<a href="{}" target="_blank" style="color: #16a34a; font-weight: bold;">📥 Descargar PDF Firmado</a>', obj.pdf_firmado.url)
        return "Pendiente"