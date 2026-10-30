# core/settings_prod.py — W03 + W11
import os
import dj_database_url
from .settings import *

# ── CONFIGURACIÓN DE DESPLIEGUE (W03) ──────────────────────────────────────
DEBUG = False

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')

# Configuración de Base de Datos PostgreSQL para Render/Heroku
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600,
        ssl_require=True
    )
}

# Archivos estáticos en producción
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Headers de seguridad
SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'True') == 'True'
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# ── ALMACENAMIENTO DE ARCHIVOS MEDIA (W11) ─────────────────────────────────
_bucket = os.environ.get('AWS_STORAGE_BUCKET_NAME', '')

if _bucket:
    DEFAULT_FILE_STORAGE  = 'storages.backends.s3boto3.S3Boto3Storage'
    AWS_ACCESS_KEY_ID     = os.environ.get('AWS_ACCESS_KEY_ID', '')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', '')
    AWS_STORAGE_BUCKET_NAME = _bucket
    AWS_S3_REGION_NAME    = os.environ.get('AWS_S3_REGION_NAME', 'us-east-1')
    AWS_DEFAULT_ACL       = None
    AWS_S3_FILE_OVERWRITE = False
    AWS_QUERYSTRING_AUTH  = False
    MEDIA_URL             = f'https://{_bucket}.s3.amazonaws.com/'