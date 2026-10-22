# core/settings.py
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

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
    # Apps del ERP
    'clientes',
    'productos',
    'proveedores',
    'ventas',
    'reportes',
    'configuracion',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Posición 1: Justo después de SecurityMiddleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
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
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

LANGUAGE_CODE = 'es-mx'
TIME_ZONE = 'America/Mexico_City'
USE_I18N = True
USE_TZ = True

# Archivos Estáticos
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

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
}

JAZZMIN_UI_TWEAKS = {
    'theme':                    'default',
    'brand_colour':             'navbar-dark',
    'accent':                   'accent-navy',
    'navbar':                   'navbar-dark',
    'sidebar':                  'sidebar-dark-navy',
}