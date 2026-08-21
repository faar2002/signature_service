import os, io
from PIL import Image, ImageDraw, ImageFont

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