# core/settings_prod.py
"""Configuración de producción — Render.com (versión final W03)."""
import os
import dj_database_url
from .settings import *   # hereda toda la configuración de settings.py

DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY', 'clave-de-prueba-local')

_render_host = os.environ.get('RENDER_EXTERNAL_HOSTNAME', '')
_extra_hosts  = os.environ.get('ALLOWED_HOSTS', '').split(',')

ALLOWED_HOSTS = ['localhost', '127.0.0.1'] + (
    [_render_host] if _render_host else []
) + [h for h in _extra_hosts if h]

if os.environ.get('DATABASE_URL'):
    DATABASES = {
        'default': dj_database_url.config(
            conn_max_age=600,
            conn_health_checks=True,
            ssl_require=True,
        )
    }

CSRF_TRUSTED_ORIGINS = []
if _render_host:
    CSRF_TRUSTED_ORIGINS.append(f'https://{_render_host}')

SECURE_SSL_REDIRECT            = True
SECURE_HSTS_SECONDS            = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD            = True
SESSION_COOKIE_SECURE          = True
CSRF_COOKIE_SECURE             = True
X_FRAME_OPTIONS                = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF    = True
SECURE_REFERRER_POLICY         = 'same-origin'

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'