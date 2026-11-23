# Sprint 7 Planning — ERP Django
## Semanas W22–W24 · Espiral 8: Calidad y Entrega

**Sprint Goal:**
Al finalizar el Sprint 7, el ERP tendrá cobertura ≥ 80%, tests
de integración para los flujos críticos, rendimiento optimizado
y documentación completa para la entrega académica final.

## HUs seleccionadas

| ID | Historia | Puntos | Semana |
|---|---|---|---|
| HU-E8-01 | Como dev, quiero cobertura de código ≥ 80% | 5 | W22 |
| HU-E8-02 | Como dev, quiero tests de integración E2E | 5 | W22 |
| HU-E8-03 | Como dev, quiero factories con datos realistas | 3 | W22 |
| HU-E8-04 | Como admin, quiero el N+1 identificado y corregido | 3 | W23 |
| HU-E8-05 | Como admin, quiero django-debug-toolbar en desarrollo | 2 | W23 |
| HU-E8-06 | Como evaluador, quiero documentación técnica completa | 3 | W24 |
| HU-E8-07 | Como evaluador, quiero el sistema desplegado y funcional | 5 | W24 |

**Total Sprint 7:** 26 puntos

## DoD — Sprint 7
- coverage report → TOTAL ≥ 80%
- 3 tests E2E pasan sin errores
- django-debug-toolbar instalado en development
- 0 queries N+1 detectadas en las vistas críticas
- README.md actualizado con instrucciones de instalación
- URL pública en Render funcionando con todos los hitos
- python manage.py test → ≥ 203 tests OK

## Sprint Backlog — actualización W22

| Tarea | Estado |
|---|---|
| pip install coverage factory-boy | ✅ W22 |
| setup.cfg: coverage config + fail_under=80 | ✅ W22 |
| tests/factories.py: factories con Faker | ✅ W22 |
| Primera corrida: cobertura basal medida (81.6%) | ✅ W22 |
| 3 tests de integración E2E | ✅ W22 |
| Tests dirigidos para brechas críticas | ✅ W22 |
| Segunda corrida: ≥ 80% de cobertura | ✅ W22 |
| htmlcov/index.html generado | ✅ W22 |
| django-debug-toolbar + análisis N+1 | ⏳ W23 |
| README.md final + documentación | ⏳ W24 |

## Sprint Backlog — actualización W23

| Tarea | Estado |
|---|---|
| Coverage ≥ 80% + factories + E2E | ✅ W22 |
| pip install django-debug-toolbar | ✅ W23 |
| debug-toolbar configurado solo en DEBUG=True | ✅ W23 |
| Auditoría SQL con panel toolbar | ✅ W23 |
| Fix N+1 en reportes/exports.py | ✅ W23 |
| Fix N+1 en ReporteVentasView | ✅ W23 |
| Fix N+1 en ProductoAdmin | ✅ W23 |
| docs/auditoria_rendimiento_w23.md | ✅ W23 |
| Tests con assertNumQueries | ✅ W23 |
| README.md final | ⏳ W24 |
| Documentación técnica | ⏳ W24 |
| Entrega final → M8 | ⏳ W24 |

# Sprint 7 Retrospective — ERP Django
## Semanas W22–W24 · Espiral 8: Calidad y Entrega

**Fecha:** 23/11/2026

## ¿Qué funcionó bien? (Keep)
1. Las factories (`factory_boy`) redujeron el código repetitivo en los tests de integración.
2. `assertNumQueries` y `CaptureQueriesContext` detectaron y previnieron regresiones N+1.
3. El bloque condicional `if DEBUG` protegió `django-debug-toolbar` sin afectar producción.

## ¿Qué mejorar? (Improve)
1. Documentar los endpoints de la API desde su creación en W10.
2. Definir presupuestos de queries SQL desde el desarrollo inicial de cada vista.

## Velocidad del Sprint 7

| HU | Pts plan. | Pts ent. |
|---|---|---|
| HU-E8-01 Cobertura ≥ 80% | 5 | 5 |
| HU-E8-02 Tests integración E2E | 5 | 5 |
| HU-E8-03 Factories datos realistas | 3 | 3 |
| HU-E8-04 Fixes N+1 | 3 | 3 |
| HU-E8-05 django-debug-toolbar | 2 | 2 |
| HU-E8-06 Documentación técnica | 3 | 3 |
| HU-E8-07 Sistema desplegado | 5 | 5 |
| **Total** | **26** | **26** |

**Velocidad Sprint 7:** 26 puntos  
**Velocidad acumulada (S0–S7):** 167 puntos