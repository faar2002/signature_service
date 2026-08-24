import base64, json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.core.files.base import ContentFile
from .models import TransaccionFirma
from .services.firma_service import generar_imagen_firma_fija, generar_imagen_firma_texto
from .services.pdf_signer_service import PDFSignerService
from .services.otp_service import OTPService

otp_service = OTPService()

def solicitar_firma_view(request):
    """
    Dashboard unificado: Separa solicitudes pendientes de firmadas.
    Ruta: /
    Template: firmas/solicitar_firma.html
    """
    pendientes = TransaccionFirma.objects.filter(estado='PENDIENTE').order_by('-fecha_creacion')
    firmadas = TransaccionFirma.objects.filter(estado='FIRMADO').order_by('-fecha_creacion')

    return render(request, 'firmas/solicitar_firma.html', {
        'pendientes': pendientes,
        'firmadas': firmadas
    })


def firmar_view(request, uuid_firma):
    transaccion = get_object_or_404(TransaccionFirma, uuid=uuid_firma)
    sesion_key = f"otp_validado_{transaccion.uuid}"
    otp_validado = request.session.get(sesion_key, False)

    if request.method == 'POST' and 'metodo_firma' in request.POST:
        metodo = request.POST.get('metodo_firma')

        if metodo == 'texto':
            texto_nombre = request.POST.get('texto_nombre', transaccion.nombre_firmante)
            estilo = request.POST.get('estilo_fuente', 'cursiva')
            
            # Generamos la firma tipográfica con la fuente elegida
            img_buffer = generar_imagen_firma_texto(texto_nombre, estilo_fuente=estilo)
            firma_archivo = ContentFile(img_buffer.read(), name=f"firma_{transaccion.uuid}.png")

        else: # metodo == 'dibujo'
            data_url = request.POST.get('base64_image')
            if not data_url or ';base64,' not in data_url:
                return JsonResponse({'status': 'error', 'message': 'Firma dibujada inválida'}, status=400)
            
            _, imgstr = data_url.split(';base64,')
            firma_archivo = ContentFile(base64.b64decode(imgstr), name=f"firma_{transaccion.uuid}.png")

        # Estampar la firma generada en el PDF
        signer = PDFSignerService(transaccion)
        ruta_relativa_pdf = signer.estampar_firma(firma_archivo)

        transaccion.pdf_firmado = ruta_relativa_pdf
        transaccion.estado = 'FIRMADO'
        transaccion.save()

        return JsonResponse({
            'status': 'success',
            'message': 'Documento firmado exitosamente',
            'uuid': str(transaccion.uuid)
        })

    pdf_url_absoluta = request.build_absolute_uri(transaccion.pdf_original.url) if transaccion.pdf_original else ""

    return render(request, 'firmas/firmar.html', {
        'transaccion': transaccion,
        'otp_validado': otp_validado,
        'pdf_url_absoluta': pdf_url_absoluta
    })


def exito_view(request, uuid_firma):
    """
    Pantalla de confirmación y descarga del PDF firmado.
    Ruta: /exito/<uuid>/
    Template: firmas/exito.html
    """
    transaccion = get_object_or_404(TransaccionFirma, uuid=uuid_firma)
    return render(request, 'firmas/exito.html', {'transaccion': transaccion})

def proceso_firma_view(request, uuid_firma):
    transaccion = get_object_or_404(TransaccionFirma, uuid=uuid_firma)
    sesion_key = f"otp_validado_{uuid_firma}"

    # 1. VERIFICAR SI YA VALIDÓ EL OTP EN ESTA SESIÓN
    if not request.session.get(sesion_key):
        if request.method == 'POST' and 'otp_code' in request.POST:
            codigo = request.POST.get('otp_code')
            if otp_service.validar_codigo(transaccion.email_firmante, codigo, "ServicioFirma"):
                request.session[sesion_key] = True
                request.session.modified = True
            else:
                return render(request, 'firmas/verificar_otp.html', {'error': 'Código inválido o expirado', 'transaccion': transaccion})

        if not request.session.get(sesion_key):
            detalle_sol_otp = otp_service.solicitar_codigo(
                email=transaccion.email_firmante,
                nombre=transaccion.nombre_firmante
            )
            
            # Manejar respuesta si viene como String con error 404/Correo Suspendido
            if isinstance(detalle_sol_otp, str):
                mensaje_error = "Servicio no disponible."
                if '{"error":' in detalle_sol_otp:
                    try:
                        json_part = detalle_sol_otp.split(' - ')[1]
                        mensaje_error = json.loads(json_part).get('error', mensaje_error)
                    except:
                        mensaje_error = detalle_sol_otp

                return render(request, 'firmas/verificar_otp.html', {'error_critico': mensaje_error, 'transaccion': transaccion})

            return render(request, 'firmas/verificar_otp.html', {'transaccion': transaccion})

    # 2. SI EL OTP YA FUE VALIDADO, PROCESAR O MOSTRAR CANVAS
    if request.method == 'POST' and 'metodo_firma' in request.POST:
        metodo = request.POST.get('metodo_firma')
        if metodo == 'nombre':
            img_buffer = generar_imagen_firma_fija(transaccion.nombre_firmante)
            firma_archivo = ContentFile(img_buffer.read(), name=f"firma_{transaccion.uuid}.png")
        else:
            data_url = request.POST.get('base64_image')
            format, imgstr = data_url.split(';base64,')
            firma_archivo = ContentFile(base64.b64decode(imgstr), name=f"firma_{transaccion.uuid}.png")

        # Aquí ejecutas tu servicio de firmado en PDF con ReportLab/PyPDF2...
        transaccion.estado = 'FIRMADO'
        transaccion.save()
        return JsonResponse({'status': 'success', 'uuid': str(transaccion.uuid)})

    # GET: Mostrar interfaz con la previsualización del nombre
    img_buffer = generar_imagen_firma_fija(transaccion.nombre_firmante)
    img_str = base64.b64encode(img_buffer.read()).decode('utf-8')
    return render(request, 'firmas/firma_canvas.html', {
        'transaccion': transaccion,
        'firma_preview': f"data:image/png;base64,{img_str}"
    })

def exito_view(request, uuid_firma):
    transaccion = get_object_or_404(TransaccionFirma, uuid=uuid_firma)
    return render(request, 'firmas/exito.html', {'transaccion': transaccion})