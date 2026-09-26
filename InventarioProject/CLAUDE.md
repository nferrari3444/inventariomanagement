# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Django 5 inventory/warehouse system (UI and domain terms are in Spanish). Single app `filsa` inside project `InventarioProject`. Custom user model `filsa.CustomUser` (`AUTH_USER_MODEL`); permissions are driven by auth Groups (e.g. Supervisor) and the `filsa/templatetags/grouptag.py` template tag.

## Commands

```bash
# Dev dependencies: Postgres + Redis (docker-compose.yml provides both)
docker-compose up -d db redis

python manage.py migrate
python manage.py runserver
python manage.py test filsa                                   # all tests
python manage.py test filsa.tests.InboundIntegrationTest      # one class
python manage.py test filsa.tests.InboundIntegrationTest.test_inbound_full_flow   # one test

# Celery worker (needed for the product CRUD bulk-upload task)
celery -A InventarioProject worker -l info
```

`django.sh` runs makemigrations + migrate + runserver. `build_files.sh` / `vercel.json` are for a Vercel deploy (Python 3.9); `dockerfile` is a simple runserver image.

## Settings / environment

- `manage.py` and `InventarioProject/celery.py` pick the settings module: `DJANGO_SETTINGS_MODULE` if set, else `settings.production` when `DJANGO_ENV=production`, else `settings.local`.
- `settings/base.py` is shared; `local.py` (Postgres via `DEV_DATABASE/DEV_USER/DEV_PASSWORD/DEV_HOST/DEV_PORT`, Celery pool `solo` for Windows) and `production.py` (Postgres via `DATABASE`, `USER`, `PASSWORD`, ..., S3 storage via `STORAGES`/`custom_storages.py`) extend it.
- Variables are read from `.env` (python-dotenv + django-environ). Tests use Postgres too — a reachable DB is required.
- Celery broker/result backend is Redis (`REDIS_URL`, default `redis://localhost:6379/0`). Emails go through SMTP (`EMAIL_HOST_PASSWORD`); tests override to the locmem backend.

## Architecture

- **Domain flows** (all in `filsa/views.py`, function-based views, routed in `filsa/urls.py`): Inbound, Outbound, Transfer. Each is a multi-step `Tasks` workflow: create (`Pending`, with `StockMovements` rows) → optional edit → reception/delivery → confirmed. **Stock (`WarehousesProduct`/`Product.quantity`) is only changed at the confirmation/reception step**, not at creation or edit. `filsa/tests_integration_doc.md` documents each flow step-by-step with expected stock at each stage — read it before changing these views.
- **Models** (`filsa/models.py`): `Product`, `WarehousesProduct` (per-warehouse stock), `Tasks`, `StockMovements`, `DiffProducts` (reception discrepancies), `Cotization`, `CrudProductTask` (status of async bulk jobs).
- **Async bulk product CRUD**: `crudProducts` view enqueues `filsa.tasks.process_crud_products` (Celery, pandas-based `_task_crear/_task_actualizar/_task_eliminar/_task_total`); the client polls `crud_task_status`. The `CrudProductTask` row is created before dispatch. `_sync_crudProducts_unused` in views.py is a legacy synchronous version kept for reference.
- **Stock list/filtering**: `StockListView` + `FilteredListView` with `filsa/filters.py`; `export_excel` for exports; `filsa/cron.py:check_stock_security` checks stock against `stockSecurity` thresholds.
- **Frontend**: Django templates in `filsa/templates/` with Tailwind (`tailwind.config.js`); several endpoints (`getProducts`, `getProductWarehouse`, `filterProducts`, ...) return JSON for in-page JS.
- `filsa/management/commands/populatedb.py` seeds data from the CSV/txt files in `filsa/management/`.
