import os
import io
from django.conf import settings
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from PyPDF2 import PdfReader, PdfWriter

class PDFSignerService:
    def __init__(self, transaccion):
        self.transaccion = transaccion

    def estampar_firma(self, firma_archivo):
        """
        Recibe el objeto de imagen de firma (ContentFile / BytesIO)
        y lo mecha en la última página del PDF original.
        """
        # 1. Obtener la ruta del PDF original
        pdf_original_path = self.transaccion.pdf_original.path

        # 2. Crear una capa PDF en memoria usando ReportLab
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)

        # Cargar la imagen de la firma (funciona con PNG transparente)
        firma_image = ImageReader(firma_archivo)

        # ---------------------------------------------------------------------
        # COORDENADAS Y TAMAÑO DE LA FIRMA
        # (En ReportLab el origen 0,0 está en la esquina INFERIOR IZQUIERDA)
        # Ajusta estas coordenadas según la plantilla de tu documento
        # ---------------------------------------------------------------------
        x = 350       # Posición horizontal desde la izquierda (puntos)
        y = 80        # Posición vertical desde abajo (puntos)
        width = 180   # Ancho del recuadro de la firma
        height = 50   # Alto del recuadro de la firma

        # Dibujar la imagen de la firma en la capa temporal
        can.drawImage(firma_image, x, y, width=width, height=height, mask='auto')

        # Opcional: Agregar metadatos / sello aclaratorio bajo la firma
        can.setFont("Helvetica", 7)
        can.setFillColorRGB(0.3, 0.3, 0.3)
        can.drawString(x, y - 10, f"Firmado digitalmente por: {self.transaccion.nombre_firmante}")
        can.drawString(x, y - 18, f"ID Doc: {self.transaccion.id_documento_externo}")
        can.drawString(x, y - 26, f"UUID: {str(self.transaccion.uuid)[:18]}...")

        can.save()
        packet.seek(0)

        # 3. Leer el PDF original y la capa de firma recién creada con PyPDF2
        pdf_reader = PdfReader(pdf_original_path)
        firma_pdf_reader = PdfReader(packet)
        pdf_writer = PdfWriter()

        num_paginas = len(pdf_reader.pages)

        # Recorrer todas las páginas del PDF original
        for i in range(num_paginas):
            pagina = pdf_reader.pages[i]
            
            # Estampar la firma ÚNICAMENTE en la última página
            if i == num_paginas - 1:
                capa_firma = firma_pdf_reader.pages[0]
                pagina.merge_page(capa_firma)
                
            pdf_writer.add_page(pagina)

        # 4. Guardar el PDF resultante en la carpeta media/docs/firmados/
        directorio_destino = os.path.join(settings.MEDIA_ROOT, 'docs', 'firmados')
        os.makedirs(directorio_destino, exist_ok=True)

        nombre_archivo_salida = f"firmado_{self.transaccion.uuid}.pdf"
        ruta_salida = os.path.join(directorio_destino, nombre_archivo_salida)

        with open(ruta_salida, 'wb') as f_out:
            pdf_writer.write(f_out)

        # Retornar la ruta relativa para el campo FileField del modelo
        return f"docs/firmados/{nombre_archivo_salida}"