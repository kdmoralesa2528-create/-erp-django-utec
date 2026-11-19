# reportes/models.py
"""Modelos de la app reportes — W20."""
from django.conf import settings
from django.db import models


class ExportacionReporte(models.Model):
    """Registro de una exportación de reporte generada en background."""

    FORMATO_CHOICES = [
        ('excel', 'Excel (.xlsx)'),
        ('pdf',   'PDF'),
    ]

    usuario    = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='exportaciones',
        verbose_name='Usuario solicitante',
    )
    formato    = models.CharField(
        max_length=10, choices=FORMATO_CHOICES, verbose_name='Formato'
    )
    filtros    = models.JSONField(
        default=dict, blank=True, verbose_name='Filtros aplicados'
    )
    archivo    = models.FileField(
        upload_to='exportaciones/', null=True, blank=True,
        verbose_name='Archivo generado'
    )
    completado = models.BooleanField(
        default=False, verbose_name='Completado'
    )
    error      = models.TextField(
        blank=True, verbose_name='Mensaje de error'
    )
    creado     = models.DateTimeField(
        auto_now_add=True, verbose_name='Fecha de solicitud'
    )

    class Meta:
        verbose_name        = 'Exportación de reporte'
        verbose_name_plural = 'Exportaciones de reportes'
        ordering            = ['-creado']

    def __str__(self) -> str:
        estado = 'completada' if self.completado else 'pendiente'
        return f'Exportación {self.get_formato_display()} #{self.pk} ({estado})'