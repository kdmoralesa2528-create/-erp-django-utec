# Sprint 6 Retrospective — ERP Django
## Semanas W19–W21 · Espiral 7: Dashboard y Reportes

**Fecha:** 19/11/2026

## ¿Qué funcionó bien? (Keep)
1. `cache.get_or_set()` con LocMemCache en tests aisló perfectamente las pruebas sin depender de Redis corriendo.
2. Extraer `generar_excel_ventas` y `generar_pdf_ventas` a `reportes/exports.py` evitó duplicar código entre la vista síncrona y la tarea async.
3. `django-simple-history` se integró limpiamente en el admin y en el detalle de producto.

## ¿Qué mejorar? (Improve)
1. El template del historial podría incluir paginación para productos con cientos de cambios de precio.
2. El umbral `UMBRAL_ASYNC` debería ser configurable desde `settings.py`, no hardcodeado en `views.py`.

## Acción de mejora (Kaizen) para Sprint 7
> "En el Sprint 7 (Pruebas de Integración), usaré factory_boy para generar datos de prueba más complejos y realistas."

## Velocidad del Sprint 6

| HU | Pts plan. | Pts ent. |
|---|---|---|
| HU-E7-01 5 KPIs del negocio | 3 | 3 |
| HU-E7-02 Gráfica últimos 7 días | 3 | 3 |
| HU-E7-03 Top 5 productos | 2 | 2 |
| HU-E7-04 Exportar filtrado Excel | 3 | 3 |
| HU-E7-05 Filtrar por fecha/cliente/producto | 2 | 2 |
| HU-E7-06 Histórico de precios | 3 | 3 |
| HU-E7-07 Dashboard < 1 segundo | 2 | 2 |
| **Total** | **18** | **18** |

**Velocidad Sprint 6:** 18 puntos
**Velocidad acumulada (S0–S6):** 141 puntos