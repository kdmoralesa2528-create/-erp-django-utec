# Análisis de Cobertura — W22
## Primera corrida: 23/11/2026
## Cobertura global inicial: 81.6%

### Brechas identificadas en la primera corrida

| Módulo | Cobertura | Líneas / ramas sin cubrir |
|---|---|---|
| reportes/tasks.py | 80.4% | Líneas 28-32, 66-73, 102-103 (ID inexistente / manejo de error) |
| reportes/models.py | 89.5% | Líneas 47-48 (`__str__` estado completado) |
| ventas/tasks.py | 90.7% | Líneas 49-52, 84-88, 202->207 (pedido inexistente / sin stock bajo) |
| ventas/views.py | 88.3% | Ramas 44->55, 67-69, 85 |
| catalogo/views.py | < 85% | `actualizar_cantidad` con 0, `vaciar_carrito`, GET en `remover` |

### Plan de acción ejecutado
- Se crearon 9 factories con `factory_boy` y `Faker('es_MX')` en `tests/factories.py`.
- Se implementaron 3 flujos completos E2E y 6 tests dirigidos en `tests/test_w22_integracion.py`.
- Se generó el reporte HTML navegable en `htmlcov/index.html` superando el umbral del 80%.