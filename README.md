Microservicio de Firma Digital (Signature Service)Este proyecto es un microservicio backend desarrollado en Python y Django para la gestión, procesamiento y estampado de firmas digitales en documentos PDF. Integra verificación de identidad de firmantes mediante un microservicio externo de OTP, lienzo interactivo de firma manuscrita y soporte para tipografías caligráficas personalizadas.🛠️ Stack TecnológicoLenguaje: Python 3.12+Framework Web: Django 5.x & Django REST FrameworkBase de Datos: PostgreSQLProcesamiento de PDFs & Gráficos: ReportLab, PyPDF2, Pillow (PIL)Lienzo Frontend: SignaturePad.js, HTML5 Canvas, Vanilla JSAutenticación Inter-servicios: API Tokens (X-System-Token)🚀 Características PrincipalesGestión de Transacciones: Creación y almacenamiento de solicitudes de firma asociadas a documentos PDF originales.Seguridad & OTP: Integración con servicio externo de validación en dos pasos (Generación y Verificación de códigos de 6 dígitos).Firma Multimodal:Trazo Manuscrito: Dibujo a mano alzada desde pantalla táctil o ratón.Tipografía Caligráfica: Estampado por nombre con fuentes tipográficas (Dancing Script, Great Vibes, Alex Brush, Montserrat).Estampado Dinámico: Inserción de sello gráfico y metadatos aclaratorios en la última página del documento PDF.Dashboard de Gestión: Tablas de control para visualizar solicitudes pendientes y descargar documentos firmados.📋 Requisitos PreviosPython 3.10 o superiorPostgreSQLGit⚙️ Instalación y Configuración Local1. Clonar el repositorioBashgit clone https://github.com/tu-usuario/signature_service.git
cd signature_service
2. Crear y activar el entorno virtualBash# Windows
python -m venv env
env\Scripts\activate

# Linux / macOS
python3 -m venv env
source env/bin/activate
3. Instalar dependenciasBashpip install -r requirements.txt
4. Configurar variables de entornoCrea un archivo .env en la raíz del proyecto basándote en el siguiente ejemplo:Fragmento de códigoDEBUG=True
SECRET_KEY=tu_secret_key_aqui
ALLOWED_HOSTS=127.0.0.1,localhost

# Base de Datos
DB_NAME=signature_db
DB_USER=postgres
DB_PASSWORD=tu_password
DB_HOST=127.0.0.1
DB_PORT=5432

# Servicio OTP Externo
OTP_SERVICE_URL=http://127.0.0.1:8000/api/v1/otp
OTP_SYSTEM_TOKEN=sys_876f57822168cd2c96d199bd426a3bf1900351cf05cf745e1a6c67e8
5. Ejecutar migracionesBashpython manage.py makemigrations
python manage.py migrate
6. Crear un superusuarioBashpython manage.py createsuperuser
7. Iniciar el servidor de desarrolloBashpython manage.py runserver 127.0.0.1:9000
📂 Estructura del ProyectoPlaintextsignature_service/
├── apps/
│   └── firmas/
│       ├── migrations/
│       ├── services/
│       │   ├── firma_service.py       # Generación de PNG con Pillow
│       │   ├── otp_service.py         # Cliente HTTP para Microservicio OTP
│       │   └── pdf_signer_service.py  # Fusión de PDF con ReportLab + PyPDF2
│       ├── templates/
│       │   └── firmas/
│       │       ├── solicitar_firma.html  # Dashboard principal
│       │       ├── firmar.html           # Interfaz OTP + Canvas
│       │       └── exito.html            # Pantalla de confirmación/descarga
│       ├── api_views.py              # Endpoints REST
│       ├── models.py                 # Transacciones y Aplicaciones Autorizadas
│       ├── urls.py                   # Vistas HTML
│       ├── urls_api.py               # Rutas API REST
│       └── views.py                  # Controladores de plantillas
├── config/                           # Configuración global de Django
├── media/                            # Archivos subidos y PDFs firmados
├── static/                           # Fuentes TTF, CSS y JS global
├── manage.py
├── requirements.txt
└── README.md
📡 Referencia de la API RESTMétodoEndpointDescripciónPOST/api/v1/transacciones/crear/Registra una nueva transacción y sube el PDF original.POST/api/v1/otp/solicitar/Solicita el envío del código de seguridad al correo.POST/api/v1/otp/validar/Verifica los 6 dígitos del código OTP.POST/firmar/<uuid>/Procesa la firma (dibujo o texto) y estampa el PDF.📄 LicenciaEste proyecto se distribuye bajo la licencia MIT. Consulta el archivo LICENSE para más detalles.