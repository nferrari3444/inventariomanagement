# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Django inventory/warehouse system (UI and domain terms are in Spanish). Single app `filsa` inside project `InventarioProject`. Custom user model `filsa.CustomUser` (`AUTH_USER_MODEL`, login by email); permissions are driven by auth Groups (`Administrador`, `Supervisor`, `Tecnico`, `Logistica`, `Comercial`) checked in templates with the `has_group` filter (`filsa/templatetags/grouptag.py`) — group names must match exactly.

The local venv (`venv/`) runs **Python 3.8 with Django 4.2**, even though `settings/base.py` says it was generated with Django 5. Keep code Python 3.8 compatible (no `X | None`, no `match`) unless the venv is upgraded; Python 3.12 is installed on the dev machine.

## Commands

Run from this directory (Windows, use the venv interpreter directly):

```bash
# Dev dependencies: Postgres + Redis (docker-compose.yml provides both)
docker-compose up -d db redis

venv/Scripts/python.exe manage.py migrate
venv/Scripts/python.exe manage.py runserver
venv/Scripts/python.exe manage.py test filsa                                   # all tests
venv/Scripts/python.exe manage.py test filsa.tests.InboundIntegrationTest      # one class
venv/Scripts/python.exe manage.py test filsa.tests.InboundIntegrationTest.test_inbound_full_flow   # one test

# Celery worker (needed for the product CRUD bulk-upload task); --pool=solo is required on Windows
venv/Scripts/celery.exe -A InventarioProject worker -l info --pool=solo

# Seed users from filsa/management/commands/usuariosFilsa.txt (idempotent; skips existing emails)
venv/Scripts/python.exe manage.py populatedb
venv/Scripts/python.exe manage.py createsuperuser   # interactive, run in a real terminal
```

`manage.py check` prints pre-existing URL warnings (`2_0.W001`, `urls.W005`); they are harmless.

`django.sh` runs makemigrations + migrate + runserver. `build_files.sh` / `vercel.json` are for a Vercel deploy (Python 3.9); `dockerfile` is a simple runserver image.

## Settings / environment

- `manage.py` and `InventarioProject/celery.py` pick the settings module: `DJANGO_SETTINGS_MODULE` if set, else `settings.production` when `DJANGO_ENV=production`, else `settings.local`.
- `settings/base.py` is shared; `local.py` (Postgres via `DEV_DATABASE/DEV_USER/DEV_PASSWORD/DEV_HOST/DEV_PORT`, Celery pool `solo` for Windows) and `production.py` (Postgres via `DATABASE`, `USER`, `PASSWORD`, ..., S3 storage via `STORAGES`/`custom_storages.py`) extend it.
- Variables are read from `.env` (python-dotenv + django-environ). Tests use Postgres too — a reachable DB is required.
- Celery broker/result backend is Redis (`REDIS_URL`, default `redis://localhost:6379/0`). Emails go through SMTP (`EMAIL_HOST_PASSWORD`); tests override to the locmem backend.
- `ANTHROPIC_API_KEY` (in `.env`, exposed as `settings.ANTHROPIC_API_KEY`) is used by the Claude API client.

## Architecture

- **Domain flows** (all in `filsa/views.py`, function-based views, routed in `filsa/urls.py`): Inbound, Outbound, Transfer. Each is a multi-step `Tasks` workflow: create (`Pending`, with `StockMovements` rows) → optional edit → reception/delivery → confirmed. **Stock (`WarehousesProduct`/`Product.quantity`) is only changed at the confirmation/reception step**, not at creation or edit. `filsa/tests_integration_doc.md` documents each flow step-by-step with expected stock at each stage — read it before changing these views.
- **Models** (`filsa/models.py`): `Product`, `WarehousesProduct` (per-warehouse stock), `Tasks`, `StockMovements`, `DiffProducts` (reception discrepancies), `Cotization`, `CrudProductTask` (status of async bulk jobs).
- **Async bulk product CRUD**: `crudProducts` view (`/products-crud/<action>`, action `crear`/`actualizar`/`eliminar`/`total`) reads an uploaded **.xlsx** with `pd.read_excel` and enqueues `filsa.tasks.process_crud_products`; the client polls `crud_task_status`. The `CrudProductTask` row is created before dispatch. Handlers read columns **by position**, so column order in the Excel matters. `total` ("Nuevo Inventario" in the menu) is the full inventory load and expects the layout of `filsa/management/ProdsFilsa.csv` (Codigo, CodigoOrigen, Concepto, Categoria, Proveedor, Producto, StockActual, per-warehouse stock/location columns, ..., price at column index 28). Note `_task_total` names one warehouse `'Joanico'` (vs `'Juanico'` elsewhere). `_sync_crudProducts_unused` in views.py is a legacy synchronous version kept for reference.
- **Stock list/filtering**: `StockListView` + `FilteredListView` with `filsa/filters.py`; `export_excel` for exports; `filsa/cron.py:check_stock_security` checks stock against `stockSecurity` thresholds (currently broken: it references the removed `Product.warehouse` field and is not scheduled anywhere).
- **Frontend**: Django templates in `filsa/templates/` with Tailwind (`tailwind.config.js`); several endpoints (`getProducts`, `getProductWarehouse`, `filterProducts`, ...) return JSON for in-page JS.
- **Seeding**: `populatedb` only loads users (lowercased emails, trimmed fields, group per `Rol`, inside a transaction). Products are loaded through the app via `crudProducts` `total`, not by this command.
- **Claude API**: `filsa/services/claude_client.py` exposes `ask_claude(prompt, system=None, model=...)` over the `anthropic` SDK (0.x, the latest that supports Python 3.8). Not wired into any view yet.

## Pending work

`RECOMENDACIONES.md` (local only, gitignored) holds the prioritized improvement backlog (security, stock correctness, permissions, performance, code quality) as a checklist. Check it before starting improvement work and tick items as they are done.
