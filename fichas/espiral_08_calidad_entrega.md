# Ficha de Sistematización — Espiral 8
## ERP Django · Espiral E8: Calidad y Entrega

| Campo | Contenido |
|---|---|
| **Número de espiral** | 8 |
| **Nombre del ciclo** | Calidad y Entrega |
| **Semanas** | W22 – W24 |
| **Asesor** | MC. Román Fernando López González |

## 1. Objetivo del ciclo
Certificar la calidad del ERP Django mediante cobertura de código ≥ 80%, tests de integración E2E, optimización de queries SQL, smoke tests y entrega de documentación técnica completa (`README.md`, `docs/API.md` y auditoría de rendimiento).

## 2. Tareas realizadas

| # | Tarea | Estado | Semana |
|---|---|---|---|
| 1 | `setup.cfg` con coverage + `fail_under=80` | ✅ | W22 |
| 2 | `tests/factories.py` con `factory_boy` | ✅ | W22 |
| 3 | Tests de integración E2E | ✅ | W22 |
| 4 | Coverage ≥ 80% alcanzado | ✅ | W22 |
| 5 | `django-debug-toolbar` configurado en `DEBUG=True` | ✅ | W23 |
| 6 | Auditoría N+1 y optimización de querysets | ✅ | W23 |
| 7 | Tests de presupuesto SQL (`test_w23_rendimiento.py`) | ✅ | W23 |
| 8 | `README.md` completo | ✅ | W24 |
| 9 | `docs/API.md` con todos los endpoints | ✅ | W24 |
| 10 | `render.yaml` con `healthCheckPath` | ✅ | W24 |
| 11 | Smoke tests (`test_w24_smoke.py`) | ✅ | W24 |

## 3. Criterios de aceptación Hito M8
- URL pública activa en Render.com: https://erp-django-utec.onrender.com
- Suite completa de pruebas pasando (`Ran 219+ tests -> OK`)
- Cobertura global ≥ 80%
- Documentación técnica completa (`README.md`, `docs/API.md`, `docs/auditoria_rendimiento_w23.md`)