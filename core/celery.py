# core/celery.py
"""Configuración de la aplicación Celery para el proyecto ERP Django."""
import os

from celery import Celery

# Establecer el módulo de settings de Django antes de crear la app Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Crear la aplicación Celery con el nombre del proyecto
app = Celery('core')

# Leer la configuración desde Django settings (prefijo CELERY_)
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-descubrir tareas en todos los archivos tasks.py de las apps instaladas
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Tarea de diagnóstico — muestra el request de la tarea."""
    print(f'Request: {self.request!r}')