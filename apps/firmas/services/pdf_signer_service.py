import os
import io
from django.conf import settings
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

class PDFSignerService:
    def __init__(self, transaccion):
        self.transaccion = transaccion

    def estampar_firma(self, archivo_firma):
        pdf_original = PdfReader(self.transaccion.pdf_original.path)
        pdf_writer = PdfWriter()

        num_paginas = len(pdf_original.pages)
        target_page = min(max(1, self.transaccion.pagina_firma), num_paginas) - 1

        # Obtener dimensiones de la página seleccionada
        page_box = pdf_original.pages[target_page].mediabox
        page_width = float(page_box.width)
        page_height = float(page_box.height)

        # Crear capa transparente con ReportLab
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=(page_width, page_height))

        # Coordenadas elegidas por el usuario
        x = self.transaccion.pos_x if self.transaccion.pos_x > 0 else 100.0
        y = self.transaccion.pos_y if self.transaccion.pos_y > 0 else 100.0

        # 1. Dibujar Imagen de la Firma (SOLO si existe archivo de firma)
        if archivo_firma is not None:
            width_firma = 140
            height_firma = 45

            if hasattr(archivo_firma, 'seek'):
                archivo_firma.seek(0)

            img_reader = ImageReader(archivo_firma.file if hasattr(archivo_firma, 'file') else archivo_firma)
            
            can.drawImage(
                img_reader, 
                x=x, 
                y=y + 35, 
                width=width_firma, 
                height=height_firma, 
                mask='auto'
            )

        # 2. Dibujar el Bloque de Leyenda Digital
        can.setFont("Helvetica-Bold", 7.5)
        can.setFillColorRGB(0.06, 0.10, 0.43) # Color azul tinta (#0f196e)
        
        uuid_str = str(self.transaccion.uuid)
        uuid_corto = f"{uuid_str[:18]}..." if len(uuid_str) > 18 else uuid_str

        can.drawString(x, y + 24, f"Firmado digitalmente por: {self.transaccion.nombre_firmante}")
        can.setFont("Helvetica", 7)
        can.setFillColorRGB(0.3, 0.3, 0.3)
        can.drawString(x, y + 13, f"ID Doc: {self.transaccion.id_documento_externo}")
        can.drawString(x, y + 3,  f"UUID: {uuid_corto}")

        can.save()
        packet.seek(0)

        # Fusionar con el PDF original
        watermark = PdfReader(packet)
        
        for i, page in enumerate(pdf_original.pages):
            if i == target_page:
                page.merge_page(watermark.pages[0])
            pdf_writer.add_page(page)

        directorio_salida = os.path.join(settings.MEDIA_ROOT, 'docs', 'firmados')
        os.makedirs(directorio_salida, exist_ok=True)

        nombre_archivo = f"Firmado_{self.transaccion.uuid}.pdf"
        ruta_salida_absoluta = os.path.join(directorio_salida, nombre_archivo)

        with open(ruta_salida_absoluta, "wb") as f:
            pdf_writer.write(f)

        return f"docs/firmados/{nombre_archivo}"