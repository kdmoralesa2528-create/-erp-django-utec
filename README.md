# ERP Django — UTEC Celaya
## Sistema de Planificación de Recursos Empresariales

![Python](https://img.shields.io/badge/python-3.11-blue)
![Django](https://img.shields.io/badge/django-4.2_LTS-green)
![Tests](https://img.shields.io/badge/tests-219+_passing-brightgreen)
![Coverage](https://img.shields.io/badge/coverage-≥80%25-yellowgreen)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

Sistema ERP académico desarrollado durante 24 semanas en el **Técnico en Programación (SEP 3061300006-23)** de UTEC Celaya.

**URL Pública:** https://erp-django-utec.onrender.com

## Características

| Módulo | Funcionalidad | Semana |
|---|---|---|
| 🏢 **Gestión de inventario** | Productos, categorías, proveedores con historial de precios | W05, W21 |
| 👥 **Clientes** | CRUD completo con validaciones | W05–W08 |
| 💰 **Ventas** | Registro, líneas de detalle, cálculo automático de totales | W05–W08 |
| 🔐 **Autenticación y roles** | Login/logout allauth + 3 grupos RBAC | W09 |
| 🌐 **API REST** | Endpoints DRF con autenticación por token | W10 |
| 🖼️ **Gestión de imágenes** | Subida con validación MIME, almacenamiento S3 | W11 |
| 📄 **Documentos** | Facturas PDF (WeasyPrint/xhtml2pdf) + exportación Excel | W12 |
| 🛒 **E-commerce** | Catálogo público, carrito de sesión, filtros | W13 |
| 💳 **Pagos Stripe** | Checkout sandbox, webhooks, descuento de stock | W14–W15 |
| ⚡ **Tareas asíncronas** | Celery + Redis: correos, alertas, reportes automáticos | W16–W18 |
| 📊 **Dashboard** | 5 KPIs + 3 gráficas Chart.js + caché Redis | W19 |
| 📋 **Reportes** | Filtros por fecha/cliente/producto + exportación adaptativa | W20 |
| 📜 **Auditoría** | Historial de cambios de precio (django-simple-history) | W21 |
| 🚀 **Calidad y Rendimiento** | Cobertura ≥ 80%, optimización N+1 y smoke tests | W22–W24 |

## Stack Tecnológico

- **Backend:** Python 3.11 · Django 4.2 LTS · Django REST Framework
- **Base de datos:** PostgreSQL 15 (producción) · SQLite (desarrollo)
- **Caché y Tareas:** Redis 7 · Celery 5.3 · Celery Beat · Flower
- **Integraciones:** Stripe (sandbox) · Brevo / SendGrid · S3
- **Frontend y Documentos:** Bootstrap 5 · Chart.js 4.4 · Jazzmin · WeasyPrint / xhtml2pdf
- **Despliegue:** Render.com (Docker)

## Instalación Rápida con Docker

```bash
git clone [https://github.com/TU_USUARIO/erp-django-utec.git](https://github.com/TU_USUARIO/erp-django-utec.git)
cd erp-django-utec
cp .env.example .env
docker-compose build
docker-compose up -d
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py crear_grupos

git clone [https://github.com/TU_USUARIO/erp-django-utec.git](https://github.com/TU_USUARIO/erp-django-utec.git)
cd erp-django-utec
python -m venv env_erp
call env_erp\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py crear_grupos
python manage.py runserver

python manage.py test tests.test_w24_smoke
python manage.py test tests
coverage run manage.py test tests && coverage report

2. **`docs/API.md`** (dentro de la carpeta `docs/`):
```markdown
# API REST — Referencia Completa
## ERP Django · UTEC Celaya

Base URL: `https://erp-django-utec.onrender.com/api/`

## Autenticación

La API usa **Token Authentication** para escritura (`POST`, `PUT`, `PATCH`, `DELETE`). Las lecturas (`GET`) son públicas.

## Endpoints

| Recurso | Rutas disponibles | Descripción |
|---|---|---|
| **Categorías** | `GET, POST /api/categorias/` · `GET, PUT, DELETE /api/categorias/{id}/` | CRUD de categorías de producto |
| **Productos** | `GET, POST /api/productos/` · `GET, PUT, PATCH, DELETE /api/productos/{id}/` | Catálogo paginado (20/pág) con `categoria_nombre`, `proveedor_nombre` e `imagen_url` |
| **Clientes** | `GET, POST /api/clientes/` · `GET, PUT, PATCH, DELETE /api/clientes/{id}/` | Gestión de clientes activos |
| **Proveedores** | `GET, POST /api/proveedores/` · `GET, PUT, DELETE /api/proveedores/{id}/` | Gestión de proveedores |
| **Ventas** | `GET, POST /api/ventas/` · `GET, DELETE /api/ventas/{id}/` | Encabezados y líneas anidadas de venta con total calculado |

## Códigos de Respuesta

- `200 OK` / `201 Created` / `204 No Content`: Operación exitosa.
- `400 Bad Request`: Datos inválidos.
- `401 Unauthorized` / `403 Forbidden`: Token faltante, inválido o sin permisos.