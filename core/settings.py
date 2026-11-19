# core/settings.py
import dj_database_url
from pathlib import Path
import os
from datetime import timedelta
from dotenv import load_dotenv
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')
SECRET_KEY = 'django-insecure-tu-clave-local'
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',        
    # Terceros
    'allauth',                     
    'allauth.account',             
    'allauth.socialaccount',       
    'rest_framework',
    'rest_framework.authtoken',
    'whitenoise.runserver_nostatic',
    'django_filters', 
    'anymail',
    # Apps del ERP
    'clientes',
    'proveedores',
    'productos',
    'ventas',
    'reportes',
    'configuracion',
    'catalogo',
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',   # ← agregar al final
]
ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'catalogo.context_processors.carrito_info',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///' + os.path.join(BASE_DIR, 'db.sqlite3'),
        conn_max_age=600
    )
}

LANGUAGE_CODE = 'es-mx'
TIME_ZONE = 'America/Mexico_City'
USE_I18N = True
USE_TZ = True

# Archivos Estáticos
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# Archivos de Media
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ── JAZZMIN — Personalización del admin con Fable 5 AzulERP ───────────────
JAZZMIN_SETTINGS = {
    'site_title':       'ERP Django',
    'site_header':      'ERP UTEC Celaya',
    'site_brand':       '📦 ERP Django',
    'welcome_sign':     'Bienvenido al Sistema ERP · UTEC Celaya',
    'copyright':        'MC. Román Fernando López González · UTEC Celaya',
    'search_model':     ['clientes.Cliente', 'productos.Producto'],
    'order_with_respect_to': [
        'clientes', 'proveedores', 'productos', 'ventas', 'configuracion', 'auth',
    ],
    'icons': {
        'auth.user':                  'fas fa-user',
        'auth.Group':                 'fas fa-users',
        'clientes.Cliente':           'fas fa-user-tie',
        'proveedores.Proveedor':      'fas fa-truck',
        'productos.Categoria':        'fas fa-tags',
        'productos.Producto':         'fas fa-box',
        'ventas.Venta':               'fas fa-file-invoice-dollar',
        'ventas.DetalleVenta':        'fas fa-list',
        'ventas.Pedido':              'fas fa-shopping-cart',
        'configuracion.ConfiguracionERP': 'fas fa-cogs',
    },
    'show_sidebar':             True,
    'navigation_expanded':      True,
    'custom_css': 'css/admin_custom.css',
}

JAZZMIN_UI_TWEAKS = {}

# ── DJANGO SITES (requerido por allauth) ──────────────────────────────────
SITE_ID = 1

# ── AUTHENTICATION BACKENDS ───────────────────────────────────────────────
AUTHENTICATION_BACKENDS = [
    # Backend estándar de Django (username + password en admin)
    'django.contrib.auth.backends.ModelBackend',
    # Backend de allauth (permite login por email también)
    'allauth.account.auth_backends.AuthenticationBackend',
]

# ── ALLAUTH: configuración para desarrollo académico ──────────────────────
ACCOUNT_LOGIN_METHODS          = {'username'}   # login por username
ACCOUNT_EMAIL_REQUIRED         = False          # no obligar correo
ACCOUNT_EMAIL_VERIFICATION     = 'none'         # no enviar email de verificación
ACCOUNT_LOGOUT_ON_GET          = True           # logout sin confirmar (dev)
ACCOUNT_SESSION_REMEMBER       = True           # recordar sesión

# LOGIN_URL y LOGIN_REDIRECT_URL ya definidos en W01:
# LOGIN_URL           = '/accounts/login/'
# LOGIN_REDIRECT_URL  = '/productos/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_REDIRECT_URL = '/productos/'
LOGIN_REDIRECT_URL = '/productos/'

# ── STRIPE (Pasarela de pago) ──────────────────────────────────────────────
STRIPE_SECRET_KEY     = os.getenv('STRIPE_SECRET_KEY', 'sk_test_placeholder')
STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY', 'pk_test_placeholder')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET', 'whsec_placeholder')



# ── CELERY — Cola de tareas asíncronas ────────────────────────────────────
# Broker: Redis almacena los mensajes de las tareas pendientes
CELERY_BROKER_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# Backend: Redis almacena los resultados de las tareas
CELERY_RESULT_BACKEND = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# Formato de serialización (JSON es seguro y portable)
CELERY_ACCEPT_CONTENT    = ['json']
CELERY_TASK_SERIALIZER   = 'json'
CELERY_RESULT_SERIALIZER = 'json'

# Zona horaria (heredar de Django)
CELERY_TIMEZONE = TIME_ZONE

# Reintentos automáticos ante fallos de conexión al broker
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

# Tiempo máximo que puede correr una tarea antes de ser terminada (segundos)
CELERY_TASK_SOFT_TIME_LIMIT = 300   # 5 minutos
CELERY_TASK_TIME_LIMIT       = 360  # 6 minutos (hard limit)

# Prefijo para las colas
CELERY_TASK_DEFAULT_QUEUE = 'erp_django'

# Para tests: ejecutar tareas sincrónicamente (sin worker)
CELERY_TASK_ALWAYS_EAGER     = False
CELERY_TASK_EAGER_PROPAGATES = True


# — EMAIL / BREVO (W17) —————————————————————————————————————
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@erp-django.com')
EMAIL_SUBJECT_PREFIX = '[ERP Django] '
ADMINS = [('Administrador', os.getenv('ADMIN_EMAIL', 'admin@erp-django.com'))]

BREVO_API_KEY = os.getenv('BREVO_API_KEY', '')
ANYMAIL = {
    'BREVO_API_KEY': BREVO_API_KEY,
}

# ── CELERY BEAT — Tareas programadas ──────────────────────────────────────
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {

    # Verificar stock bajo cada hora
    'verificar-stock-bajo-cada-hora': {
        'task':     'ventas.verificar_stock_bajo',
        'schedule': timedelta(hours=1),
        'args':     (5,),   # umbral = 5 unidades
        'options':  {'queue': 'erp_django'},
    },

    # Reporte de ventas diario a las 8:00 AM (hora México)
    'reporte-ventas-diario-8am': {
        'task':     'ventas.reporte_ventas_diario',
        'schedule': crontab(hour=8, minute=0),
        'options':  {'queue': 'erp_django'},
    },

}

# Necesario para que Beat use la zona horaria de Django (no UTC)
CELERY_BEAT_TIMEZONE = TIME_ZONE   # 'America/Mexico_City'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}