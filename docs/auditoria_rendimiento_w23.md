# Auditoría de Rendimiento SQL — W23
## ERP Django · UTEC Celaya
## Fecha: 23/11/2026

## Método de medición
- `django-debug-toolbar` panel SQL en el navegador
- `connection.queries` y `assertNumQueries` en tests automatizados
- Dataset: 20 ventas con detalles asociados

## Resultados del diagnóstico

### Vista: Lista de ventas (`/ventas/`)
| | Queries | Tiempo aprox. |
|---|---|---|
| **Antes** | 3 (`select_related` aplicado desde W07) | 12ms |
| **Después** | 3 — sin cambios necesarios | 12ms |
| Fix aplicado | Ninguno — ya optimizado desde W07 | — |

### Vista: Reporte de ventas (`/reportes/ventas/`)
| | Queries | Tiempo aprox. |
|---|---|---|
| **Antes** | 22 (1 ventas + 20 detalles + 1 cliente) | 48ms |
| **Después** | 3 (`prefetch_related('detalles__producto')`) | 14ms |
| Fix aplicado | `prefetch_related('detalles__producto')` en `get_queryset()` |

### Función: `generar_excel_ventas()` con 50 ventas
| | Queries | Tiempo aprox. |
|---|---|---|
| **Antes** | 201 (1 + 50 detalles + 150 productos) | 380ms |
| **Después** | 3 (`prefetch_related` en el queryset recibido) | 28ms |
| Fix aplicado | `prefetch_related('detalles__producto')` en `exportar_reporte()` y `generar_exportacion_async()` |

### Admin: Lista de productos (`/admin/productos/producto/`)
| | Queries | Tiempo aprox. |
|---|---|---|
| **Antes** | 41 (1 + 20 categoria + 20 proveedor) | 62ms |
| **Después** | 1 (`list_select_related`) | 8ms |
| Fix aplicado | `list_select_related = ('categoria', 'proveedor')` en `ProductoAdmin` |

## Resumen del impacto

| Escenario | Queries antes | Queries después | Mejora |
|---|---|---|---|
| Reporte ventas (20 ventas) | 22 | 3 | 86% menos queries |
| Export Excel (50 ventas) | 201 | 3 | 99% menos queries |
| Admin productos (20 items) | 41 | 1 | 98% menos queries |