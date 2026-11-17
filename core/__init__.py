# core/__init__.py
"""Inicialización del paquete core del proyecto ERP Django."""
from .celery import app as celery_app

__all__ = ('celery_app',)