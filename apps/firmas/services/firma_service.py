import os, io
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings

FUENTES_DISPONIBLES = {
    'cursiva': os.path.join(settings.BASE_DIR, 'static/fonts/DancingScript-Regular.ttf'),
    'elegante': os.path.join(settings.BASE_DIR, 'static/fonts/GreatVibes-Regular.ttf'),
    'clasica': os.path.join(settings.BASE_DIR, 'static/fonts/AlexBrush-Regular.ttf'),
    'formal': os.path.join(settings.BASE_DIR, 'static/fonts/Montserrat-BoldItalic.ttf'),
}

def generar_imagen_firma_texto(nombre_texto, estilo_fuente='cursiva'):
    """
    Genera un PNG en memoria con el nombre en la tipografía seleccionada.
    """
    width, height = 500, 150
    # Crear imagen PNG transparente (RGBA)
    imagen = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(imagen)

    # Obtener ruta de la fuente elegida
    ruta_fuente = FUENTES_DISPONIBLES.get(estilo_fuente, FUENTES_DISPONIBLES['cursiva'])

    try:
        font = ImageFont.truetype(ruta_fuente, 42)
    except Exception:
        # Fallback si no encuentra el archivo .ttf especificado
        font = ImageFont.load_default()

    # Obtener dimensiones del texto para centrarlo correctamente
    bbox = draw.textbbox((0, 0), nombre_texto, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = (width - text_width) / 2
    y = (height - text_height) / 2 - bbox[1]

    # Dibujar el texto en color azul tinta (#0f196e)
    color_tinta = (15, 25, 110, 255)
    draw.text((x, y), nombre_texto, fill=color_tinta, font=font)

    # Guardar la imagen en un buffer BytesIO
    buffer = io.BytesIO()
    imagen.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer

def generar_imagen_firma_fija(nombre):
    width, height = 600, 150
    img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    ruta_fuente = os.path.join("assets", "fonts", "DancingScript-Regular.ttf")
    try:
        font = ImageFont.truetype(ruta_fuente, 85)
    except OSError:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), nombre, font=font)
    text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    
    draw.text(((width - text_w) / 2, (height - text_h) / 2), 
              nombre, font=font, fill=(15, 25, 110, 255))
    
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf