# Ficha de Sistematización — Espiral 7
## ERP Django · Espiral E7: Dashboard y Reportes

| Campo | Contenido |
|---|---|
| **Número de espiral** | 7 |
| **Nombre del ciclo** | Dashboard y Reportes |
| **Semanas** | W19 – W21 |
| **Fecha de inicio** | 05/11/2026 |
| **Fecha de cierre** | 19/11/2026 |
| **Responsable** | [Tu Nombre] |
| **Asesor** | MC. Román Fernando López González |

## 1. Objetivo del ciclo
Implementar un módulo de inteligencia de negocio con dashboard de KPIs cacheados, reportes filtrables con exportación adaptativa, e histórico completo de cambios de precio.

## 2. Tareas realizadas

| # | Tarea | Estado | Semana |
|---|---|---|---|
| 1 | CACHES con Redis (DB separada del broker) | ✅ | W19 |
| 2 | _calcular_kpis(): 5 KPIs + 3 datasets | ✅ | W19 |
| 3 | DashboardView con cache.get_or_set() | ✅ | W19 |
| 4 | Template dashboard.html + 3 gráficas Chart.js | ✅ | W19 |
| 5 | reportes/filters.py: VentaReporteFilter | ✅ | W20 |
| 6 | reportes/models.py: ExportacionReporte | ✅ | W20 |
| 7 | ReporteVentasView + exportación síncrona | ✅ | W20 |
| 8 | reportes/exports.py (funciones reutilizables) | ✅ | W20 |
| 9 | Exportación asíncrona > UMBRAL_ASYNC | ✅ | W20 |
| 10 | django-simple-history instalado | ✅ | W21 |
| 11 | HistoricalRecords en Producto, Venta, Pedido | ✅ | W21 |
| 12 | HistoricoProductoView + template timeline | ✅ | W21 |
| 13 | Migraciones históricas aplicadas y 182 tests OK | ✅ | W21 |

## 3. Evidencias
- Dashboard: `/reportes/` → 5 KPIs + 3 gráficas
- Caché: segunda carga < 100ms
- Exportación: `/reportes/exportar/?formato=excel` → descarga inmediata
- Histórico: `/productos/<id>/historico/` → timeline de cambios
- Admin: botón "History" en cada producto
- Tests: Suite completa acumulada (182 tests) → OK

## 4. Criterios de aceptación

| Criterio | Estado |
|---|---|
| GET /reportes/ → 5 KPIs cacheados | ✅ |
| 3 gráficas Chart.js renderizadas | ✅ |
| Reporte filtrado por fecha/cliente/producto | ✅ |
| Exportación Excel síncrona | ✅ |
| Exportación asíncrona > 1000 filas | ✅ |
| Histórico de precios en timeline | ✅ |
| history_type '+' en creación, '~' en edición | ✅ |
| diff_against() detecta campo precio | ✅ |
| Suite de tests acumulada OK | ✅ |

## 5. Problemas encontrados
- En W20 fue necesario instalar `openpyxl` y `xhtml2pdf` en el entorno virtual local y mockear `.delay` para probar el estado pendiente cuando `CELERY_TASK_ALWAYS_EAGER=True`.
- En W21 se aisló `CACHES` con `LocMemCache` y Celery en `memory://` durante `manage.py test` para evitar dependencia de Redis activo en laboratorio, y se normalizó `requirements.txt` a UTF-8.

## 6. Lecciones aprendidas
1. Separar la lógica de exportación (`exports.py`) permite compartirla entre vistas síncronas y tareas Celery sin duplicar código.
2. `HistoryRequestMiddleware` debe ir después de `AuthenticationMiddleware` para que `history_user` registre al usuario autenticado.
3. Aislar cachés y brokers en memoria bajo `if 'test' in sys.argv:` garantiza reproducibilidad en cualquier entorno.

## 7. Tiempo total invertido

| Categoría | Horas |
|---|---|
| Diseño | 1.5 |
| Implementación | 4.5 |
| Pruebas | 2.0 |
| Documentación | 1.0 |
| **Total Espiral 7** | **9.0** |