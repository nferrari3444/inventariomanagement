# Integration Tests Documentation

## Overview

Integration tests for the three main inventory flows: **Inbound**, **Outbound**, and **Transfer**.
Each test simulates the full request chain through Django — from the initial task creation, through an optional edit, to the final confirmation — asserting stock quantities at every stage.

All integration test classes use `@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')` to prevent real emails from being sent during test runs.

---

## Inbound Flow — `InboundIntegrationTest`

**Class:** `filsa.tests.InboundIntegrationTest`
**Test method:** `test_inbound_full_flow`

### Setup
| Object | Details |
|---|---|
| User | Supervisor group, `inbound_integration@example.com` |
| Product | `internalCode=10001`, `quantity=0` |
| Warehouse | `Deposito Inbound`, `quantity=0` |

### Steps

#### Step 1 — Create inbound task (`POST /inbound/`)
- Submits product name, internal code, quantity, warehouse, and reason (`motivoIngreso`).
- **Asserts:**
  - Response is `302` (redirect to tasks list).
  - A `Task` is created with `status='Pending'` and `actionType='Nuevo Ingreso'`.
  - One `StockMovement` is created linked to the task.
  - Warehouse quantity remains `0` (stock is not updated until reception is confirmed).

#### Step 2 — Edit the task (`POST /inbound-edit/<task_id>`)
- Updates `department` to `'Logística'` and `motivoIngreso` to `'Importación'`.
- **Asserts:**
  - Response is `302`.
  - Task fields are updated in the database.
  - Warehouse quantity is still `0` (edit does not affect stock).

#### Step 3 — Confirm reception (`POST /inbound-reception/<task_id>`)
- Submits `cantidadNeta_0=10` (net quantity received). Other fields (warehouse, product, department, etc.) are read automatically from the task instance by the form.
- **Asserts:**
  - Response is `302`.
  - Task `status` is `'Confirmed'`.
  - Warehouse quantity is updated to `10.0`.
  - Global product quantity is updated to `10.0`.

---

## Outbound Flow — `OutboundIntegrationTest`

**Class:** `filsa.tests.OutboundIntegrationTest`
**Test method:** `test_outbound_full_flow`

### Setup
| Object | Details |
|---|---|
| User | Supervisor group, `outbound_integration@example.com` |
| Product | `internalCode=10002`, `quantity=50` |
| Warehouse | `Deposito Outbound`, `quantity=50` |

### Steps

#### Step 1 — Create outbound order task (`POST /outbound-order/`)
- Submits product name, internal code, quantity (`15`), warehouse, and reason (`motivoEgreso`).
- **Asserts:**
  - Response is `302`.
  - A `Task` is created with `status='Pending'` and `actionType='Nuevo Egreso'`.
  - One `StockMovement` is created linked to the task.
  - Warehouse quantity remains `50` (stock is not updated until delivery is confirmed).

#### Step 2 — Edit the task (`POST /task-edited/<task_id>`)
- Updates `department` to `'Logística'` and `motivoEgreso` to `'Planta de Armado'`.
- **Asserts:**
  - Response is `302`.
  - Task fields are updated in the database.
  - Warehouse quantity is still `50`.

#### Step 3 — Confirm delivery (`POST /outbound-delivery/<task_id>`)
- Submits `cantidadNeta_0=15`. Other fields are read automatically from the task instance.
- **Asserts:**
  - Response is `302`.
  - Task `status` is `'Confirmed'`.
  - Warehouse quantity is updated to `35.0` (`50 - 15`).
  - Global product quantity is updated to `35.0`.

---

## Transfer Flow — `TransferIntegrationTest`

**Class:** `filsa.tests.TransferIntegrationTest`
**Test method:** `test_transfer_full_flow`

This is the most complex flow. When a transfer is created, the product quantity is placed in a special `'En Transito'` warehouse entry. On confirmation, stock is moved from the source warehouse to the destination warehouse and the `'En Transito'` entry is deleted.

### Setup
| Object | Details |
|---|---|
| User | Supervisor group, `transfer_integration@example.com` |
| Product | `internalCode=10003`, `quantity=30` |
| Source warehouse | `Source Deposito`, `quantity=20` |
| Destination warehouse | `Dest Deposito`, `quantity=10` |

### Steps

#### Step 1 — Create transfer task (`POST /transfer/`)
- Submits product name, internal code, quantity to transfer (`5`), and source warehouse.
- **Asserts:**
  - Response is `302`.
  - A `Task` is created with `status='Pending'` and `actionType='Transferencia'`.
  - One `StockMovement` is created linked to the task.
  - Source warehouse quantity is still `20` (not yet deducted).
  - A new `WarehousesProduct` entry named `'En Transito'` is created for the product with `quantity=5`.

#### Step 2 — Edit the task (`POST /transfer-edit/<task_id>`)
- Updates `department` to `'Logística'`.
- **Asserts:**
  - Response is `302`.
  - Task `department` is updated.
  - Source warehouse quantity is still `20` (no stock changes during edit).

#### Step 3 — Confirm transfer reception (`POST /transfer-reception/<task_id>`)
- Submits `warehouse` (destination warehouse name), `cantidadNeta_0=5`. The source warehouse (`warehouseSalida`) is read automatically from the task instance.
- **Asserts:**
  - Response is `302`.
  - Task `status` is `'Confirmed'`.
  - Source warehouse quantity is reduced to `15.0` (`20 - 5`).
  - Destination warehouse quantity is increased to `15.0` (`10 + 5`).
  - The `'En Transito'` `WarehousesProduct` entry for this product is deleted.

---

## Key Design Notes

### Why `cantidadNeta` must be submitted explicitly
The reception and delivery forms override `value_from_datadict` on most fields (warehouse, product name, quantity, department, date, etc.) to read directly from the task instance stored in the database. This means those fields do **not** need to come from the POST request. The only field that must be explicitly submitted is `cantidadNeta_{i}` (0-indexed per product), which is the net quantity actually received or delivered.

### Bug found during test development
The integration test for transfer caught a real bug: `'Confirma Transferencia'` (22 characters) was being written to `Tasks.actionType`, which had `max_length=20`. This would cause a `StringDataRightTruncation` error in PostgreSQL on any confirmed transfer. The field was fixed by increasing `max_length` to `30` in `filsa/models.py` and a new migration (`0002_increase_actiontype_max_length.py`) was generated.

---

## Running the Tests

```bash
# Run only integration tests
python manage.py test filsa.tests.InboundIntegrationTest filsa.tests.OutboundIntegrationTest filsa.tests.TransferIntegrationTest

# Run all tests (unit + integration)
python manage.py test filsa.tests
```
