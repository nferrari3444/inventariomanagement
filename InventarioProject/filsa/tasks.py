"""
Celery tasks for asynchronous CRUD operations on products.

Each task replicates the synchronous logic that previously ran inside the
crudProducts view, but without access to the HTTP request.  Results and
error messages are persisted to CrudProductTask so the UI can poll for
status via the crud_task_status endpoint.
"""

from __future__ import annotations

import logging
from functools import reduce
from operator import or_

from django.db import DatabaseError
import pandas as pd
from celery import shared_task
from django.core.exceptions import ValidationError
from django.db.models import F, Q
from django.utils import timezone

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Internal helpers – replicate the synchronous view logic
# ─────────────────────────────────────────────────────────────────────────────

def _rebuild_df(rows: list[list]) -> pd.DataFrame:
    """Reconstruct a positional DataFrame from the serialised row list."""
    df = pd.DataFrame(rows)
    # Restore None for any NaN that crept in during JSON round-trip
    return df.astype(object).where(pd.notnull(df), None)


def _task_crear(df: pd.DataFrame) -> dict:
    """Create new products (Product + WarehousesProduct)."""
    from .models import Product, WarehousesProduct

    logger.info('crear: starting – %d rows received', len(df))

    products_warehouse: list[WarehousesProduct] = []

    for i in range(len(df)):
        try:
            product_code   = df.iloc[i][1]
            product_qty    = _parse_numeric(df.iloc[i][3])
            product_price  = _parse_price(df.iloc[i][7])
            deposit        = df.iloc[i][9]
            product_barcode = df.iloc[i][2]
            name           = df.iloc[i][0]
            category       = df.iloc[i][4]
            supplier       = df.iloc[i][5] if df.iloc[i][5] is not None else ''
            stock_security = _parse_numeric(df.iloc[i][6])
            currency       = df.iloc[i][8]
            location       = df.iloc[i][10] if df.iloc[i][10] is not None else ''

            logger.debug(
                'crear: row %d – code=%s name=%s category=%s deposit=%s qty=%s',
                i, product_code, name, category, deposit, product_qty,
            )

            if Product.objects.filter(internalCode=product_code).exists():
                logger.warning('crear: row %d – product code %s already exists', i, product_code)
                return {
                    'success': False,
                    'error': (
                        f'El Producto con codigo {product_code} ya existe en la base '
                        f'de datos'
                    ),
                    'extra_tags': 'product_exists',
                }

            new_product = Product.objects.create(
                name=name,
                internalCode=product_code,
                barcode=product_barcode,
                quantity=product_qty,
                price=product_price,
                category=category,
                supplier=supplier,
                stockSecurity=stock_security,
                currency=currency,
            )
            logger.info('crear: row %d – product %s (code=%s) created', i, name, product_code)
            products_warehouse.append(
                WarehousesProduct(
                    product=new_product,
                    name=deposit,
                    quantity=product_qty,
                    location=location,
                    deltaQuantity=0,
                )
            )

        except (ValidationError, ValueError, KeyError, IndexError, DatabaseError) as exc:
            logger.error('crear: row %d – error: %s', i, exc)
            return {
                'success': False,
                'error': (
                    f'Creacion de Producto con codigo {product_code} es incorrecta. '
                    f'Chequear campos. Los campos Codigo Interno, Nombre, Categoría y Moneda, son obligatorios'
                    f'Error details: {str(exc)}'),
                'extra_tags': 'product format',
            }

    WarehousesProduct.objects.bulk_create(products_warehouse)
    logger.info('crear: finished – %d products created', len(products_warehouse))
    return {
        'success': True,
        'message': f'Se crean {len(products_warehouse)} productos',
    }


def _task_actualizar(df: pd.DataFrame) -> dict:
    """Update quantity and price for existing products."""
    from .models import Product, WarehousesProduct

    logger.info('actualizar: starting – %d rows received', len(df))

    for i in range(len(df)):
        try:
            product_code = df.iloc[i][0]
            product_qty  = df.iloc[i][1]
            product_price = df.iloc[i][2]
            deposit      = df.iloc[i][3]

            logger.debug(
                'actualizar: row %d – code=%s deposit=%s qty=%s price=%s',
                i, product_code, deposit, product_qty, product_price,
            )

            Product.objects.filter(internalCode=product_code).update(
                quantity=F('quantity') + product_qty,
                price=product_price,
            )

            wp = WarehousesProduct.objects.get(
                name=deposit, product__internalCode=product_code
            )
            wp.quantity = product_qty
            wp.save()
            logger.info('actualizar: row %d – product code %s updated', i, product_code)

        except WarehousesProduct.DoesNotExist:
            logger.error(
                'actualizar: row %d – product code %s not found in deposit %s',
                i, product_code, deposit,
            )
            return {
                'success': False,
                'error': (
                    f'Actualización de Productos con codigo {product_code} es '
                    f'incorrecta. Chequear si el producto existe en deposito {deposit}'
                ),
                'extra_tags': 'product format',
            }

    logger.info('actualizar: finished – %d products updated', len(df))
    return {
        'success': True,
        'message': f'Se actualizan {len(df)} productos',
    }


def _task_eliminar(df: pd.DataFrame) -> dict:
    """Delete products from both Product and WarehousesProduct (via CASCADE)."""
    from .models import Product

    logger.info('eliminar: starting – %d rows received', len(df))

    products_deleted = 0
    for i in range(len(df)):
        try:
            product_code = df.iloc[i][0]
            logger.debug('eliminar: row %d – deleting product code %s', i, product_code)

            Product.objects.filter(internalCode=product_code).delete()
            products_deleted += 1
            logger.info('eliminar: row %d – product code %s deleted', i, product_code)

        except Product.DoesNotExist:
            logger.error('eliminar: row %d – product code %s not found', i, product_code)
            return {
                 'success': False,
                 'error': (
                     f'Eliminación de Producto con codigo {product_code} es '
                     f'incorrecta. Chequear si el producto existe'
                 ),
                 'extra_tags': 'product format',
             }

    logger.info('eliminar: finished – %d products deleted', products_deleted)
    return {
        'success': True,
        'message': f'Se eliminan {products_deleted} productos',
    }
        # If the product doesn't exist, consider it already "deleted" and skip

        # except Product.DoesNotExist:
        #

def _parse_numeric(raw, default=0) -> float:
    """Parse a value that may use European decimal notation (1.234,56 → 1234.56)."""
    if raw is None or raw == '':
        return default
    s = str(raw).replace(',', '.')
    try:
        return float(s)
    except ValueError:
        return default


def _parse_price(raw):
    """
    Parse a price cell that may contain 'USD', dashes, or European formatting.
    Returns a float or None.
    """
    if raw is None or raw == '':
        return None
    price_str = (
        str(raw)
        .strip('USD').strip()
        .replace('-', '')
        .replace('#¡REF! ', '')
        .replace('#¡REF!', '')
    )
    if price_str in ('', 'None'):
        return None
    try:
        return float(price_str.replace('.', '').replace(',', '.'))
    except ValueError:
        return None


def _task_total(df: pd.DataFrame) -> dict:
    """
    Full inventory generation: create or update every product and its warehouse
    quantities from the standard inventory Excel sheet.
    """
    from .models import Product, WarehousesProduct
    from .views import update_product_warehouse, create_products_warehouse

    logger.info('total: starting – %d rows received, %d columns', len(df), len(df.columns))

    processed = 0

    for i in range(len(df)):
        try:
            product_code        = df.iloc[i][0]
            product_code_origin = df.iloc[i][1]
            category            = df.iloc[i][3]
            supplier            = df.iloc[i][4]
            product_name        = df.iloc[i][5]

            # Skip rows with missing name or category
            if (
                pd.isna(product_name) or product_name in ('', None)
                or pd.isna(category) or category in ('', None)
            ):
                logger.debug('total: row %d – skipped (empty name or category)', i)
                continue

            logger.debug(
                'total: row %d – code=%s name=%s category=%s supplier=%s',
                i, product_code, product_name, category, supplier,
            )

            stock          = _parse_numeric(df.iloc[i][6])
            stock_security = _parse_numeric(df.iloc[i][15])
            price          = _parse_price(df.iloc[i][28])

            warehouse_1 = 'Anaya 2710'
            warehouse_2 = 'Crocker'
            warehouse_3 = 'Joanico'
            warehouse_4 = 'In Transit'

            qty_1  = _parse_numeric(df.iloc[i][7])
            loc_1  = df.iloc[i][8]
            qty_2  = _parse_numeric(df.iloc[i][9])
            loc_2  = df.iloc[i][10]
            qty_3  = _parse_numeric(df.iloc[i][11])
            loc_3  = df.iloc[i][12]
            qty_4  = _parse_numeric(df.iloc[i][14])
            loc_4  = 'Transito'

            deposits = [warehouse_1, warehouse_2, warehouse_3, warehouse_4]
            wh_quantities = [
                (warehouse_1, qty_1, loc_1),
                (warehouse_2, qty_2, loc_2),
                (warehouse_3, qty_3, loc_3),
                (warehouse_4, qty_4, loc_4),
            ]

            product_exists = Product.objects.filter(internalCode=product_code).exists()
            wh_exists = WarehousesProduct.objects.filter(
                product__internalCode=product_code, name__in=deposits
            ).exists()

            if product_exists or wh_exists:
                logger.info('total: row %d – updating existing product code %s', i, product_code)
                p = Product.objects.filter(internalCode=product_code).first()
                p.category      = category
                p.supplier      = supplier
                p.stockSecurity = stock_security
                p.quantity      = stock
                p.price         = price
                p.name          = product_name
                p.save()
                update_product_warehouse(deposits, p.internalCode, wh_quantities)
                logger.info('total: row %d – product code %s updated', i, product_code)
            else:
                logger.info('total: row %d – creating new product code %s', i, product_code)
                p = Product.objects.create(
                    name=product_name,
                    internalCode=product_code,
                    barcode=product_code_origin,
                    quantity=stock,
                    price=price,
                    category=category,
                    supplier=supplier,
                    stockSecurity=stock_security,
                )
                create_products_warehouse(deposits, p.internalCode, wh_quantities)
                logger.info('total: row %d – product code %s created', i, product_code)

            processed += 1

        except Exception as exc:
            print(f'error in creating product {product_code}: error is: {exc}')
            logger.warning(
                'total: row %d – error for product code %s, skipping: %s',
                i,
                df.iloc[i][0] if len(df.columns) > 0 else '?',
                exc,
            )

    logger.info('total: finished – %d products processed out of %d rows', processed, len(df))
    return {
        'success': True,
        'message': f'Se crean o actualizan {processed} productos',
    }


# ─────────────────────────────────────────────────────────────────────────────
# Public Celery task
# ─────────────────────────────────────────────────────────────────────────────

@shared_task(bind=True)
def process_crud_products(self, action: str, rows: list[list], user_id: int) -> dict:
    """
    Asynchronously execute a CRUD operation on products.

    Parameters
    ----------
    action : str
        One of 'crear', 'actualizar', 'eliminar', 'total'.
    rows : list[list]
        Serialised DataFrame rows (df.values.tolist() after NaN → None conversion).
    user_id : int
        ID of the user who triggered the operation (for audit purposes).
    """
    from .models import CrudProductTask

    logger.info(
        'process_crud_products: task_id=%s action=%s user_id=%s rows=%d',
        self.request.id, action, user_id, len(rows),
    )

    task_record = CrudProductTask.objects.filter(task_id=self.request.id).first()

    # Mark as started
    if task_record:
        task_record.status = CrudProductTask.STATUS_STARTED
        task_record.save(update_fields=['status'])

    try:
        df = _rebuild_df(rows)
        print('DataFrame rebuilt in task – shape is {}'.format(df.shape))
        print('DataFrame head:\n{}'.format(df.head()))
        logger.info('process_crud_products: DataFrame rebuilt – %d rows, %d columns', len(df), len(df.columns))

        dispatch = {
            'crear':      _task_crear,
            'actualizar': _task_actualizar,
            'eliminar':   _task_eliminar,
            'total':      _task_total,
        }

        handler = dispatch.get(action)
        if handler is None:
            logger.error('process_crud_products: unknown action=%s', action)
            result = {'success': False, 'error': f'Acción desconocida: {action}'}
        else:
            result = handler(df)

    except Exception as exc:
        logger.exception('process_crud_products failed for action=%s', action)
        result = {'success': False, 'error': str(exc)}
        if task_record:
            task_record.status       = CrudProductTask.STATUS_FAILURE
            task_record.error_message = str(exc)
            task_record.completed_at  = timezone.now()
            task_record.save(update_fields=['status', 'error_message', 'completed_at'])
        raise

    # Persist final status
    if task_record:
        task_record.status         = (
            CrudProductTask.STATUS_SUCCESS if result['success']
            else CrudProductTask.STATUS_FAILURE
        )
        task_record.result_message = result.get('message', '')
        task_record.error_message  = result.get('error', '')
        task_record.completed_at   = timezone.now()
        task_record.save(update_fields=[
            'status', 'result_message', 'error_message', 'completed_at'
        ])

    logger.info(
        'process_crud_products: task_id=%s action=%s finished – success=%s message=%s error=%s',
        self.request.id, action, result.get('success'), result.get('message'), result.get('error'),
    )
    return result
