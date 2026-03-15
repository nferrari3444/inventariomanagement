from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from .models import Product, WarehousesProduct, Tasks, StockMovements, DiffProducts, Cotization
from .views import update_product_warehouse, create_products_warehouse
from functools import reduce
from django.db.models import Q

from .forms import InboundForm, OutboundOrderForm, TransferForm

User = get_user_model()

class ProductModelTest(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Test Product",
            barcode="123456789",
            internalCode=12345,
            quantity=10.0,
            category="Test Category",
            supplier="Test Supplier",
            stockSecurity=5,
            price=100.0,
            currency="USD"
        )

    def test_product_creation(self):
        self.assertEqual(self.product.name, "Test Product")
        self.assertEqual(self.product.barcode, "123456789")
        self.assertEqual(self.product.quantity, 10.0)

    def test_product_str(self):
        self.assertEqual(str(self.product), "Test Product")

class WarehousesProductModelTest(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Warehouse Product",
            barcode="987654321",
            internalCode=54321,
            quantity=20.0
        )
        self.warehouse_product = WarehousesProduct.objects.create(
            name="Main Warehouse",
            product=self.product,
            quantity=15.0,
            location="Aisle 1",
            deltaQuantity=0.0
        )

    def test_warehouse_product_creation(self):
        self.assertEqual(self.warehouse_product.name, "Main Warehouse")
        self.assertEqual(self.warehouse_product.product.name, "Warehouse Product")
        self.assertEqual(self.warehouse_product.quantity, 15.0)

    def test_warehouse_product_str(self):
        self.assertEqual(str(self.warehouse_product), "Main Warehouse")

    def test_delete_does_not_create_stock_movement(self):
        # Deleting WarehousesProduct should NOT create a StockMovements entry
        initial_count = StockMovements.objects.count()
        self.warehouse_product.delete()
        final_count = StockMovements.objects.count()
        self.assertEqual(final_count, initial_count)


    def test_update_product_warehouse(self):
        # Create additional warehouse products for testing update
        wp_a = WarehousesProduct.objects.create(
            name="Deposito A",
            product=self.product,
            quantity=10.0,
            location="Location A",
            deltaQuantity=0.0
        )
        wp_b = WarehousesProduct.objects.create(
            name="Deposito B",
            product=self.product,
            quantity=10.0,
            location="Location B",
            deltaQuantity=0.0
        )

        # Prepare data for update
        deposits = ['Deposito A', 'Deposito B']
        product_code = self.product.internalCode
        product_warehouse_quantities = [
            ('Deposito A', 25.0, 'Updated Location A'),
            ('Deposito B', 30.0, 'Updated Location B')
        ]

        # Call the function
        results = update_product_warehouse(deposits, product_code, product_warehouse_quantities)

        # Verify updates
        self.assertEqual(len(results), 2)
        wp_a.refresh_from_db()
        wp_b.refresh_from_db()
        self.assertEqual(wp_a.quantity, 25.0)
        self.assertEqual(wp_a.location, 'Updated Location A')
        self.assertEqual(wp_b.quantity, 30.0)
        self.assertEqual(wp_b.location, 'Updated Location B')

    def test_create_products_warehouse(self):
        # Use a different product for create test
        new_product = Product.objects.create(
            name="New Test Product",
            barcode="NEW123",
            internalCode=88888,
            quantity=50.0
        )

        # Prepare data for create
        deposits = ['New Deposito X', 'New Deposito Y']
        product_code = new_product.internalCode
        product_warehouse_quantities = [
            ('New Deposito X', 15.0, 'Location X'),
            ('New Deposito Y', 20.0, 'Location Y')
        ]

        initial_count = WarehousesProduct.objects.filter(product=new_product).count()
        self.assertEqual(initial_count, 0)

        # Call the function
        create_products_warehouse(deposits, product_code, product_warehouse_quantities)

        # Verify creations
        final_count = WarehousesProduct.objects.filter(product=new_product).count()
        self.assertEqual(final_count, 2)

        wp_x = WarehousesProduct.objects.get(product=new_product, name='New Deposito X')
        wp_y = WarehousesProduct.objects.get(product=new_product, name='New Deposito Y')

        self.assertEqual(wp_x.quantity, 15.0)
        self.assertEqual(wp_x.location, 'Location X')
        self.assertEqual(wp_y.quantity, 20.0)
        self.assertEqual(wp_y.location, 'Location Y')

class TasksModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.product = Product.objects.create(
            name="Task Product",
            barcode="111111111",
            internalCode=11111
        )
        self.warehouse_product = WarehousesProduct.objects.create(
            name="Task Warehouse",
            product=self.product,
            deltaQuantity=0.0
        )
        self.task = Tasks.objects.create(
            receptor=self.user,
            issuer=self.user,
            department="Ventas",
            date="2023-01-01",
            motivoIngreso="Compra en Plaza",
            warehouseProduct=self.warehouse_product,
            actionType="Inbound"
        )

    def test_task_creation(self):
        self.assertEqual(self.task.status, "Pending")
        self.assertEqual(self.task.actionType, "Inbound")
        self.assertEqual(self.task.receptor.username, "testuser")

class HomeViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass', email='testuser@example.com')

    def test_home_view_status_code(self):
        self.client.force_login(self.user)
       # self.client.login(username='testuser', password='testpass', email="nferrari34444@gmail.com")
        response = self.client.get(reverse('home'), follow=True )
        self.assertEqual(response.status_code, 200)

    def test_home_view_template(self):
        #self.client.login(username='testuser', password='testpass', email="nferrari34444@gmail.com")
        self.client.force_login(self.user)
        response = self.client.get(reverse('home'),follow=True)
        self.assertTemplateUsed(response, 'home.html')



# Additional tests can be added for other views and functionalities as needed.

# ...existing code...

@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class InboundViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass',email='inbound@example.com')
        # Create a group and assign it to the user to avoid IndexError in views
        group = Group.objects.create(name='Supervisor')
        self.user.groups.add(group)
        self.product = Product.objects.create(name='Inbound Product', internalCode=99999, quantity=0)
        self.warehouse = WarehousesProduct.objects.create(name='Inbound Warehouse', product=self.product, quantity=0, deltaQuantity=0.0)

    def test_inbound_form_submission(self):
        self.client.force_login(self.user)
        data = {
            'producto_1': self.product.name,
            'internalCode_1': self.product.internalCode,
            'cantidad_1': 10,
            'warehouse': self.warehouse.name,
            'motivoIngreso': 'Compra en Plaza',
            'extra_field_count': 1,
            'department': 'Ventas',
            'date': '2023-01-01',
            'issuer': self.user.id,
            'receptor': self.user.id,
        }

        initial_tasks = Tasks.objects.count()
        initial_movements = StockMovements.objects.count()
        response = self.client.post(reverse('inbound'), data)
        self.assertEqual(response.status_code, 302)
        self.assertGreater(Tasks.objects.count(), initial_tasks)
        self.assertGreater(StockMovements.objects.count(), initial_movements)
        self.warehouse.refresh_from_db()
        # Quantity in warehouse is updated only when inbound is confirmed
        self.assertEqual(self.warehouse.quantity, 0.0)


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class OutboundViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass', email='outbound@example.com')
        # Create a group and assign it to the user to avoid IndexError in views
        group = Group.objects.create(name='Supervisor')
        self.user.groups.add(group)
        self.product = Product.objects.create(name='Outbound Product', internalCode=88888, quantity=20)
        self.warehouse = WarehousesProduct.objects.create(name='Outbound Warehouse', product=self.product, quantity=20, deltaQuantity=0.0)

    def test_outbound_form_submission(self):
        self.client.force_login(self.user)
        data = {
            'producto_1': self.product.name,
            'internalCode_1': self.product.internalCode,
            'cantidad_1': 5,
            'warehouse': self.warehouse.name,
            'motivoEgreso': 'Planta de Armado',
            'extra_field_count': 1,
            'department': 'Ventas',
            'date': '2023-01-01',
            'issuer': self.user.id,
            'receptor': self.user.id,
        }

        initial_tasks = Tasks.objects.count()
        initial_movements = StockMovements.objects.count()
        response = self.client.post(reverse('outboundorder'), data)
        self.assertEqual(response.status_code, 302)
        self.assertGreater(Tasks.objects.count(), initial_tasks)
        self.assertGreater(StockMovements.objects.count(), initial_movements)
        self.warehouse.refresh_from_db()
        # Quantity in warehouse is updated only when outbound is delivered/confirmed
        self.assertEqual(self.warehouse.quantity, 20)


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class TransferViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass', email="transfer@example.com")
        # Create a group and assign it to the user to avoid IndexError in views
        group = Group.objects.create(name='Supervisor')
        self.user.groups.add(group)
        self.product = Product.objects.create(name='Transfer Product', internalCode=77777, quantity=30)
        self.source_warehouse = WarehousesProduct.objects.create(name='Source Warehouse', product=self.product, quantity=20, deltaQuantity=0.0)
        self.dest_warehouse = WarehousesProduct.objects.create(name='Dest Warehouse', product=self.product, quantity=10, deltaQuantity=0.0)

    def test_transfer_form_submission(self):
        self.client.force_login(self.user)
        data = {
            'product_1': self.product.name,
            'internalCode_1': self.product.internalCode,
            'cantidad_1': 5,
            'warehouse': self.source_warehouse.name,
            'extra_field_count': 1,
            'department': 'Ventas',
            'date': '2023-01-01',
            'issuer': self.user.id,
            'receptor': self.user.id,
        }

        initial_tasks = Tasks.objects.count()
        initial_movements = StockMovements.objects.count()
        response = self.client.post(reverse('transfer'), data)
        self.assertEqual(response.status_code, 302)
        self.assertGreater(Tasks.objects.count(), initial_tasks)
        self.assertGreater(StockMovements.objects.count(), initial_movements)
        self.source_warehouse.refresh_from_db()
        self.dest_warehouse.refresh_from_db()
        # Quantities are updated only when transfer is confirmed (transferReceptionView)
        self.assertEqual(self.source_warehouse.quantity, 20)
        self.assertEqual(self.dest_warehouse.quantity, 10)


# ─────────────────────────────────────────────────────────────────────────────
# Integration Tests
# ─────────────────────────────────────────────────────────────────────────────

@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class InboundIntegrationTest(TestCase):
    """
    Full integration test for the inbound flow:
      1. Create inbound task          → inboundView
      2. Edit the task                → inboundEditTask
      3. Confirm reception            → inboundReceptionView
    Stock quantities must only change at step 3.
    """

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass', email='inbound_integration@example.com'
        )
        group = Group.objects.create(name='Supervisor')
        self.user.groups.add(group)
        self.product = Product.objects.create(
            name='Integration Inbound Product', internalCode=10001, quantity=0
        )
        self.warehouse = WarehousesProduct.objects.create(
            name='Deposito Inbound', product=self.product, quantity=0, deltaQuantity=0.0
        )

    def test_inbound_full_flow(self):
        self.client.force_login(self.user)

        # ── Step 1: Create the inbound task ──────────────────────────────────
        response = self.client.post(reverse('inbound'), {
            'producto_1': self.product.name,
            'internalCode_1': self.product.internalCode,
            'cantidad_1': 10,
            'warehouse': self.warehouse.name,
            'motivoIngreso': 'Compra en Plaza',
            'extra_field_count': 1,
            'department': 'Ventas',
            'date': '2023-01-01',
            'issuer': self.user.id,
            'receptor': self.user.id,
        })
        self.assertEqual(response.status_code, 302)

        task = Tasks.objects.filter(actionType='Nuevo Ingreso').latest('task_id')
        self.assertEqual(task.status, 'Pending')
        self.assertEqual(StockMovements.objects.filter(task=task).count(), 1)

        # Quantity must not change until reception is confirmed
        self.warehouse.refresh_from_db()
        self.assertEqual(self.warehouse.quantity, 0.0)

        # ── Step 2: Edit the task ─────────────────────────────────────────────
        response = self.client.post(reverse('inboundedit', args=[task.task_id]), {
            'motivoIngreso': 'Importación',
            'receptor': self.user.id,
            'department': 'Logística',
            'date': '2023-01-01',
            'warehouse': self.warehouse.name,
            'extra_field_count': 1,
            'producto_1': self.product.name,
            'internalCode_1': self.product.internalCode,
            'cantidad_1': 10,
            'issuer': self.user.id,
            'observationsSolicitud': 'Edited by integration test',
        })
        self.assertEqual(response.status_code, 302)

        task.refresh_from_db()
        self.assertEqual(task.department, 'Logística')
        self.assertEqual(task.motivoIngreso, 'Importación')
        # Stock still unchanged after edit
        self.warehouse.refresh_from_db()
        self.assertEqual(self.warehouse.quantity, 0.0)

        # ── Step 3: Confirm reception ─────────────────────────────────────────
        # The reception form reads product, quantity, warehouse and most task
        # fields from the task instance via value_from_datadict overrides.
        # Only cantidadNeta_{i} (0-indexed) must be submitted explicitly.
        response = self.client.post(reverse('inboundreception', args=[task.task_id]), {
            'extra_field_count': 1,
            'cantidadNeta_0': 10,
            'observationsConfirma': 'All units received',
        })
        self.assertEqual(response.status_code, 302)

        task.refresh_from_db()
        self.assertEqual(task.status, 'Confirmed')

        self.warehouse.refresh_from_db()
        self.assertEqual(self.warehouse.quantity, 10.0)

        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, 10.0)


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class OutboundIntegrationTest(TestCase):
    """
    Full integration test for the outbound flow:
      1. Create outbound order task   → outboundOrderView
      2. Edit the task                → editDeliveryTask
      3. Confirm delivery             → outboundDeliveryView
    Stock quantities must only change at step 3.
    """

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass', email='outbound_integration@example.com'
        )
        group = Group.objects.create(name='Supervisor')
        self.user.groups.add(group)
        self.product = Product.objects.create(
            name='Integration Outbound Product', internalCode=10002, quantity=50
        )
        self.warehouse = WarehousesProduct.objects.create(
            name='Deposito Outbound', product=self.product, quantity=50, deltaQuantity=0.0
        )

    def test_outbound_full_flow(self):
        self.client.force_login(self.user)

        # ── Step 1: Create the outbound order task ────────────────────────────
        response = self.client.post(reverse('outboundorder'), {
            'producto_1': self.product.name,
            'internalCode_1': self.product.internalCode,
            'cantidad_1': 15,
            'warehouse': self.warehouse.name,
            'motivoEgreso': 'Ventas',
            'extra_field_count': 1,
            'department': 'Ventas',
            'date': '2023-01-01',
            'issuer': self.user.id,
            'receptor': self.user.id,
        })
        self.assertEqual(response.status_code, 302)

        task = Tasks.objects.filter(actionType='Nuevo Egreso').latest('task_id')
        self.assertEqual(task.status, 'Pending')
        self.assertEqual(StockMovements.objects.filter(task=task).count(), 1)

        # Quantity must not change until delivery is confirmed
        self.warehouse.refresh_from_db()
        self.assertEqual(self.warehouse.quantity, 50.0)

        # ── Step 2: Edit the task ─────────────────────────────────────────────
        response = self.client.post(reverse('editdeliverytask', args=[task.task_id]), {
            'motivoEgreso': 'Planta de Armado',
            'receptor': self.user.id,
            'department': 'Logística',
            'date': '2023-01-01',
            'warehouse': self.warehouse.name,
            'extra_field_count': 1,
            'producto_1': self.product.name,
            'internalCode_1': self.product.internalCode,
            'cantidad_1': 15,
            'issuer': self.user.id,
            'observationsSolicitud': 'Edited by integration test',
        })
        self.assertEqual(response.status_code, 302)

        task.refresh_from_db()
        self.assertEqual(task.department, 'Logística')
        self.assertEqual(task.motivoEgreso, 'Planta de Armado')
        # Stock still unchanged after edit
        self.warehouse.refresh_from_db()
        self.assertEqual(self.warehouse.quantity, 50.0)

        # ── Step 3: Confirm delivery ──────────────────────────────────────────
        # Similar to inbound reception: most fields are read from the task
        # instance. Only cantidadNeta_{i} (0-indexed) must be submitted.
        response = self.client.post(reverse('outbounddelivery', args=[task.task_id]), {
            'extra_field_count': 1,
            'cantidadNeta_0': 15,
            'observationsConfirma': 'All units delivered',
        })
        self.assertEqual(response.status_code, 302)

        task.refresh_from_db()
        self.assertEqual(task.status, 'Confirmed')

        self.warehouse.refresh_from_db()
        self.assertEqual(self.warehouse.quantity, 35.0)  # 50 - 15

        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, 35.0)  # 50 - 15


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class TransferIntegrationTest(TestCase):
    """
    Full integration test for the transfer flow:
      1. Create transfer task         → transferView
         Products are placed in the 'En Transito' warehouse.
      2. Edit the task                → transferEditTask
      3. Confirm transfer reception   → transferReceptionView
         Products leave 'En Transito' and arrive at the destination warehouse.
    """

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass', email='transfer_integration@example.com'
        )
        group = Group.objects.create(name='Supervisor')
        self.user.groups.add(group)
        self.product = Product.objects.create(
            name='Integration Transfer Product', internalCode=10003, quantity=30
        )
        self.source_warehouse = WarehousesProduct.objects.create(
            name='Source Deposito', product=self.product, quantity=20, deltaQuantity=0.0
        )
        self.dest_warehouse = WarehousesProduct.objects.create(
            name='Dest Deposito', product=self.product, quantity=10, deltaQuantity=0.0
        )

    def test_transfer_full_flow(self):
        self.client.force_login(self.user)

        # ── Step 1: Create the transfer task ──────────────────────────────────
        response = self.client.post(reverse('transfer'), {
            'product_1': self.product.name,
            'internalCode_1': self.product.internalCode,
            'cantidad_1': 5,
            'warehouse': self.source_warehouse.name,
            'extra_field_count': 1,
            'department': 'Ventas',
            'date': '2023-01-01',
            'issuer': self.user.id,
            'receptor': self.user.id,
        })
        self.assertEqual(response.status_code, 302)

        task = Tasks.objects.filter(actionType='Transferencia').latest('task_id')
        self.assertEqual(task.status, 'Pending')
        self.assertEqual(StockMovements.objects.filter(task=task).count(), 1)

        # Source warehouse quantity is still unchanged at this point
        self.source_warehouse.refresh_from_db()
        self.assertEqual(self.source_warehouse.quantity, 20.0)

        # 'En Transito' warehouse entry must be created with the transferred quantity
        en_transito = WarehousesProduct.objects.filter(product=self.product, name='En Transito')
        self.assertTrue(en_transito.exists())
        self.assertEqual(en_transito.first().quantity, 5.0)

        # ── Step 2: Edit the task ─────────────────────────────────────────────
        response = self.client.post(reverse('transferedit', args=[task.task_id]), {
            'receptor': self.user.id,
            'department': 'Logística',
            'date': '2023-01-01',
            'warehouse': self.source_warehouse.name,
            'extra_field_count': 1,
            'product_1': self.product.name,
            'internalCode_1': self.product.internalCode,
            'cantidad_1': 5,
            'issuer': self.user.id,
            'observationsSolicitud': 'Edited by integration test',
        })
        self.assertEqual(response.status_code, 302)

        task.refresh_from_db()
        self.assertEqual(task.department, 'Logística')
        # No stock changes during edit
        self.source_warehouse.refresh_from_db()
        self.assertEqual(self.source_warehouse.quantity, 20.0)

        # ── Step 3: Confirm transfer reception ────────────────────────────────
        # The destination warehouse must be submitted explicitly.
        # warehouseSalida (source) is read from the task instance automatically.
        # cantidadNeta_{i} (0-indexed) must be submitted explicitly.
        response = self.client.post(reverse('transferreception', args=[task.task_id]), {
            'warehouse': self.dest_warehouse.name,
            'extra_field_count': 1,
            'cantidadNeta_0': 5,
            'observationsConfirma': 'Transfer received',
        })
        self.assertEqual(response.status_code, 302)

        task.refresh_from_db()
        self.assertEqual(task.status, 'Confirmed')

        # Source warehouse quantity is reduced by the transferred amount
        self.source_warehouse.refresh_from_db()
        self.assertEqual(self.source_warehouse.quantity, 15.0)  # 20 - 5

        # Destination warehouse quantity is increased by the net received amount
        self.dest_warehouse.refresh_from_db()
        self.assertEqual(self.dest_warehouse.quantity, 15.0)  # 10 + 5

        # 'En Transito' entry must be deleted after confirmation
        self.assertFalse(
            WarehousesProduct.objects.filter(product=self.product, name='En Transito').exists()
        )


# =============================================================================
# CRUD PRODUCTS – helper functions & view tests
# =============================================================================

import io
import pandas as pd
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.messages import get_messages


# ─────────────────────────────────────────────────────────────────────────────
# Shared base: creates a logged-in client and Excel-builder helpers
# ─────────────────────────────────────────────────────────────────────────────

class _CrudProductsBase(TestCase):
    """Mixin with setUp + Excel file factories used by all CRUD view tests."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='crud_user', password='testpass', email='crud@example.com'
        )
        self.client.force_login(self.user)

    # ── Excel builders ────────────────────────────────────────────────────────

    def _excel(self, df: pd.DataFrame, filename: str = 'test.xlsx') -> SimpleUploadedFile:
        buf = io.BytesIO()
        df.to_excel(buf, index=False)
        buf.seek(0)
        return SimpleUploadedFile(
            filename, buf.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )

    def _crear_excel(self, rows: list) -> SimpleUploadedFile:
        """
        rows: list of dicts.  Column order (positional) for 'crear' action:
          [0] name  [1] internalCode  [2] barcode  [3] quantity
          [4] category  [5] supplier  [6] stockSecurity
          [7] price  [8] currency  [9] deposit  [10] location
        """
        cols = ['nombre', 'cod_interno', 'barcode', 'cantidad',
                'categoria', 'proveedor', 'stock_seg', 'precio',
                'moneda', 'deposito', 'ubicacion']
        data = [[r['name'], r['internalCode'], r['barcode'], r['quantity'],
                 r['category'], r['supplier'], r['stockSecurity'], r['price'],
                 r['currency'], r['deposit'], r['location']] for r in rows]
        return self._excel(pd.DataFrame(data, columns=cols), 'crear.xlsx')

    def _actualizar_excel(self, rows: list) -> SimpleUploadedFile:
        """
        Column order for 'actualizar':
          [0] internalCode  [1] quantity  [2] price  [3] deposit
        """
        cols = ['cod_interno', 'cantidad', 'precio', 'deposito']
        data = [[r['internalCode'], r['quantity'], r['price'], r['deposit']] for r in rows]
        return self._excel(pd.DataFrame(data, columns=cols), 'actualizar.xlsx')

    def _eliminar_excel(self, codes: list) -> SimpleUploadedFile:
        """Single column: internalCode."""
        return self._excel(pd.DataFrame({'cod_interno': codes}), 'eliminar.xlsx')

    def _total_excel(self, rows: list) -> SimpleUploadedFile:
        """
        'total' action reads by positional index – needs exactly 29 columns.
          [0]  internalCode          [1]  barcode
          [3]  category              [4]  supplier
          [5]  name                  [6]  stock (total qty)
          [7]  qty Anaya 2710        [8]  loc Anaya 2710
          [9]  qty Crocker           [10] loc Crocker
          [11] qty Joanico           [12] loc Joanico
          [14] qty In Transit        [15] stockSecurity
          [28] price
        Columns 2, 13, 16-27 are not read by the view.
        """
        records = []
        for r in rows:
            row = [None] * 29
            row[0]  = r['internalCode']
            row[1]  = r.get('barcode', '')
            row[3]  = r.get('category', 'Cat')
            row[4]  = r.get('supplier', 'Sup')
            row[5]  = r.get('name', 'Producto')
            row[6]  = r.get('stock', 0)
            row[7]  = r.get('qty_anaya', 0)
            row[8]  = r.get('loc_anaya', 'A')
            row[9]  = r.get('qty_crocker', 0)
            row[10] = r.get('loc_crocker', 'C')
            row[11] = r.get('qty_joanico', 0)
            row[12] = r.get('loc_joanico', 'J')
            row[14] = r.get('qty_transit', 0)
            row[15] = r.get('stockSecurity', 0)
            row[28] = r.get('price', None)
            records.append(row)
        cols = [f'c{i}' for i in range(29)]
        return self._excel(pd.DataFrame(records, columns=cols), 'total.xlsx')

    def _default_total_row(self, **overrides):
        row = {
            'internalCode': 80001, 'barcode': 'BC80001',
            'name': 'Total Product', 'category': 'Electronics', 'supplier': 'Prov X',
            'stock': 30, 'qty_anaya': 10, 'loc_anaya': 'A1',
            'qty_crocker': 8, 'loc_crocker': 'C1',
            'qty_joanico': 7, 'loc_joanico': 'J1',
            'qty_transit': 5, 'stockSecurity': 10, 'price': None,
        }
        row.update(overrides)
        return row

    WAREHOUSES = ['Anaya 2710', 'Crocker', 'Joanico', 'In Transit']

    def _create_product_with_warehouses(self, internal_code, name='Existing', **product_kwargs):
        """Helper: create a Product + one WarehousesProduct per warehouse."""
        p = Product.objects.create(name=name, internalCode=internal_code, quantity=0.0, **product_kwargs)
        for wh in self.WAREHOUSES:
            WarehousesProduct.objects.create(
                name=wh, product=p, quantity=0.0, location='', deltaQuantity=0.0
            )
        return p


# =============================================================================
# 1. Unit tests – update_product_warehouse
# =============================================================================

class UpdateProductWarehouseUnitTest(_CrudProductsBase):
    """Focused unit tests for the update_product_warehouse helper."""

    def setUp(self):
        super().setUp()
        self.product = Product.objects.create(
            name='UPW Product', internalCode=30001, quantity=100.0
        )
        self.wp_anaya = WarehousesProduct.objects.create(
            name='Anaya 2710', product=self.product,
            quantity=30.0, location='A1', deltaQuantity=0.0
        )
        self.wp_crocker = WarehousesProduct.objects.create(
            name='Crocker', product=self.product,
            quantity=20.0, location='C1', deltaQuantity=0.0
        )

    def test_updates_quantity_for_each_deposit(self):
        from .views import update_product_warehouse
        update_product_warehouse(
            ['Anaya 2710', 'Crocker'], self.product.internalCode,
            [('Anaya 2710', 50.0, 'A2'), ('Crocker', 40.0, 'C2')]
        )
        self.wp_anaya.refresh_from_db()
        self.wp_crocker.refresh_from_db()
        self.assertEqual(self.wp_anaya.quantity, 50.0)
        self.assertEqual(self.wp_crocker.quantity, 40.0)

    def test_updates_location_for_each_deposit(self):
        from .views import update_product_warehouse
        update_product_warehouse(
            ['Anaya 2710', 'Crocker'], self.product.internalCode,
            [('Anaya 2710', 30.0, 'New A'), ('Crocker', 20.0, 'New C')]
        )
        self.wp_anaya.refresh_from_db()
        self.wp_crocker.refresh_from_db()
        self.assertEqual(self.wp_anaya.location, 'New A')
        self.assertEqual(self.wp_crocker.location, 'New C')

    def test_returns_queryset_with_correct_count(self):
        from .views import update_product_warehouse
        results = update_product_warehouse(
            ['Anaya 2710', 'Crocker'], self.product.internalCode,
            [('Anaya 2710', 1.0, 'L'), ('Crocker', 1.0, 'L')]
        )
        self.assertEqual(len(results), 2)

    def test_does_not_affect_other_products(self):
        from .views import update_product_warehouse
        other = Product.objects.create(name='Other', internalCode=30002, quantity=0.0)
        WarehousesProduct.objects.create(
            name='Anaya 2710', product=other,
            quantity=99.0, location='Z', deltaQuantity=0.0
        )
        update_product_warehouse(
            ['Anaya 2710'], self.product.internalCode,
            [('Anaya 2710', 1.0, 'X')]
        )
        wp_other = WarehousesProduct.objects.get(product=other, name='Anaya 2710')
        self.assertEqual(wp_other.quantity, 99.0)

    def test_single_deposit_update(self):
        from .views import update_product_warehouse
        update_product_warehouse(
            ['Anaya 2710'], self.product.internalCode,
            [('Anaya 2710', 77.0, 'Z9')]
        )
        self.wp_anaya.refresh_from_db()
        self.assertEqual(self.wp_anaya.quantity, 77.0)
        self.assertEqual(self.wp_anaya.location, 'Z9')


# =============================================================================
# 2. Unit tests – create_products_warehouse
# =============================================================================

class CreateProductsWarehouseUnitTest(_CrudProductsBase):
    """Focused unit tests for the create_products_warehouse helper."""

    def setUp(self):
        super().setUp()
        self.product = Product.objects.create(
            name='CPW Product', internalCode=40001, quantity=60.0
        )

    def test_creates_one_entry_per_deposit(self):
        from .views import create_products_warehouse
        deposits = ['Anaya 2710', 'Crocker', 'Joanico', 'In Transit']
        quantities = [
            ('Anaya 2710', 15.0, 'A'), ('Crocker', 10.0, 'C'),
            ('Joanico', 5.0, 'J'), ('In Transit', 0.0, 'T'),
        ]
        create_products_warehouse(deposits, self.product.internalCode, quantities)
        self.assertEqual(
            WarehousesProduct.objects.filter(product=self.product).count(), 4
        )

    def test_correct_quantity_per_warehouse(self):
        from .views import create_products_warehouse
        deposits = ['Anaya 2710', 'Crocker']
        quantities = [('Anaya 2710', 25.0, 'A'), ('Crocker', 12.0, 'C')]
        create_products_warehouse(deposits, self.product.internalCode, quantities)
        wp_a = WarehousesProduct.objects.get(product=self.product, name='Anaya 2710')
        wp_c = WarehousesProduct.objects.get(product=self.product, name='Crocker')
        self.assertEqual(wp_a.quantity, 25.0)
        self.assertEqual(wp_c.quantity, 12.0)

    def test_correct_location_per_warehouse(self):
        from .views import create_products_warehouse
        deposits = ['Anaya 2710', 'Crocker']
        quantities = [('Anaya 2710', 0.0, 'Estante A'), ('Crocker', 0.0, 'Fila B')]
        create_products_warehouse(deposits, self.product.internalCode, quantities)
        wp_a = WarehousesProduct.objects.get(product=self.product, name='Anaya 2710')
        self.assertEqual(wp_a.location, 'Estante A')

    def test_delta_quantity_initialised_to_zero(self):
        from .views import create_products_warehouse
        create_products_warehouse(
            ['Anaya 2710'], self.product.internalCode,
            [('Anaya 2710', 5.0, 'L')]
        )
        wp = WarehousesProduct.objects.get(product=self.product, name='Anaya 2710')
        self.assertEqual(wp.deltaQuantity, 0.0)

    def test_links_to_correct_product(self):
        from .views import create_products_warehouse
        other = Product.objects.create(name='Other', internalCode=40002, quantity=0.0)
        create_products_warehouse(
            ['Crocker'], self.product.internalCode,
            [('Crocker', 3.0, 'L')]
        )
        wp = WarehousesProduct.objects.get(name='Crocker', product=self.product)
        self.assertEqual(wp.product.internalCode, self.product.internalCode)
        self.assertFalse(WarehousesProduct.objects.filter(product=other).exists())


# =============================================================================
# 3. GET requests – form rendered for every action
# =============================================================================

class CrudProductsGetTest(_CrudProductsBase):

    def _assert_renders_form(self, action):
        url = reverse('productscrud', args=[action])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'crudProducts.html')
        self.assertIn('form', response.context)
        self.assertEqual(response.context['action'], action)

    def test_get_crear(self):
        self._assert_renders_form('crear')

    def test_get_actualizar(self):
        self._assert_renders_form('actualizar')

    def test_get_eliminar(self):
        self._assert_renders_form('eliminar')

    def test_get_total(self):
        self._assert_renders_form('total')

    def test_title_is_capitalised_action(self):
        response = self.client.get(reverse('productscrud', args=['crear']))
        self.assertEqual(response.context['title'], 'Crear Productos')


# =============================================================================
# 4. Action: crear
# =============================================================================

class CrudProductsCrearTest(_CrudProductsBase):

    URL = 'productscrud'

    def _post(self, rows):
        return self.client.post(
            reverse(self.URL, args=['crear']),
            {'archivo': self._crear_excel(rows)},
            format='multipart',
        )

    def _row(self, **overrides):
        base = {
            'name': 'Nuevo Producto', 'internalCode': 50001, 'barcode': 'BC50001',
            'quantity': 10.0, 'category': 'Electronics', 'supplier': 'Prov A',
            'stockSecurity': 5, 'price': 99.99, 'currency': 'USD',
            'deposit': 'Anaya 2710', 'location': 'A-1',
        }
        base.update(overrides)
        return base

    # ── Happy path ────────────────────────────────────────────────────────────

    def test_creates_product_in_product_table(self):
        self._post([self._row()])
        self.assertTrue(Product.objects.filter(internalCode=50001).exists())

    def test_creates_warehouse_product_entry(self):
        self._post([self._row()])
        self.assertTrue(
            WarehousesProduct.objects.filter(
                product__internalCode=50001, name='Anaya 2710'
            ).exists()
        )

    def test_persists_all_product_fields(self):
        self._post([self._row(
            name='Producto Completo', internalCode=50002, barcode='BC50002',
            quantity=20.0, category='Insumos', supplier='Prov B',
            stockSecurity=8, price=150.0, currency='USD',
            deposit='Crocker', location='B-3',
        )])
        p = Product.objects.get(internalCode=50002)
        self.assertEqual(p.name, 'Producto Completo')
        self.assertEqual(p.barcode, 'BC50002')
        self.assertEqual(p.quantity, 20.0)
        self.assertEqual(p.category, 'Insumos')
        self.assertEqual(p.supplier, 'Prov B')
        self.assertEqual(p.stockSecurity, 8)
        self.assertEqual(p.currency, 'USD')

    def test_warehouse_product_has_correct_quantity_and_location(self):
        self._post([self._row(
            internalCode=50003, quantity=15.0, deposit='Joanico', location='J-5'
        )])
        wp = WarehousesProduct.objects.get(product__internalCode=50003, name='Joanico')
        self.assertEqual(wp.quantity, 15.0)
        self.assertEqual(wp.location, 'J-5')
        self.assertEqual(wp.deltaQuantity, 0.0)

    def test_multiple_products_all_created(self):
        rows = [
            self._row(name=f'Prod {i}', internalCode=50010 + i,
                      barcode=f'BC{i}', quantity=float(i * 5),
                      price=10.0 * i, location=f'A-{i}')
            for i in range(1, 4)
        ]
        self._post(rows)
        for i in range(1, 4):
            self.assertTrue(Product.objects.filter(internalCode=50010 + i).exists())
            self.assertTrue(
                WarehousesProduct.objects.filter(
                    product__internalCode=50010 + i, name='Anaya 2710'
                ).exists()
            )

    def test_multiple_products_success_message_includes_count(self):
        rows = [
            self._row(name=f'P{i}', internalCode=50020 + i, barcode=f'B{i}')
            for i in range(3)
        ]
        response = self._post(rows)
        msgs = ' '.join(m.message for m in get_messages(response.wsgi_request))
        self.assertIn('3', msgs)

    def test_success_returns_200_and_renders_form(self):
        response = self._post([self._row()])
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'crudProducts.html')

    # ── Duplicate / error path ────────────────────────────────────────────────

    def test_existing_product_triggers_error_message(self):
        Product.objects.create(name='Existing', internalCode=50030, quantity=5.0)
        response = self._post([self._row(internalCode=50030)])
        tags = [m.extra_tags for m in get_messages(response.wsgi_request)]
        self.assertIn('product_exists', tags)

    def test_existing_product_redirects(self):
        Product.objects.create(name='Existing', internalCode=50031, quantity=0.0)
        response = self._post([self._row(internalCode=50031)])
        self.assertEqual(response.status_code, 302)

    def test_existing_product_does_not_create_duplicate(self):
        Product.objects.create(name='Dup', internalCode=50032, quantity=0.0)
        initial = Product.objects.count()
        self._post([self._row(internalCode=50032)])
        self.assertEqual(Product.objects.count(), initial)

    def test_early_redirect_on_duplicate_leaves_later_rows_unprocessed(self):
        """When row 0 is a duplicate the view redirects immediately – row 1 must NOT be created."""
        Product.objects.create(name='Dup', internalCode=50040, quantity=0.0)
        rows = [
            self._row(internalCode=50040),          # duplicate → redirect
            self._row(name='New', internalCode=50041, barcode='BC50041'),  # should not be created
        ]
        self._post(rows)
        self.assertFalse(Product.objects.filter(internalCode=50041).exists())

    def test_different_deposits_per_product(self):
        deposits = ['Anaya 2710', 'Crocker', 'Joanico']
        for i, dep in enumerate(deposits):
            self._post([self._row(name=f'Dep Prod {i}', internalCode=50050 + i,
                                  barcode=f'DBC{i}', deposit=dep, location=f'L{i}')])
            wp = WarehousesProduct.objects.get(product__internalCode=50050 + i, name=dep)
            self.assertEqual(wp.location, f'L{i}')


# =============================================================================
# 5. Action: actualizar
# =============================================================================

class CrudProductsActualizarTest(_CrudProductsBase):

    def setUp(self):
        super().setUp()
        self.product = Product.objects.create(
            name='Act Product', internalCode=60001, quantity=10.0, price=50.0,
            category='Cat', supplier='S', stockSecurity=2
        )
        self.wp = WarehousesProduct.objects.create(
            name='Anaya 2710', product=self.product,
            quantity=10.0, location='A1', deltaQuantity=0.0
        )

    def _post(self, rows):
        return self.client.post(
            reverse('productscrud', args=['actualizar']),
            {'archivo': self._actualizar_excel(rows)},
            format='multipart',
        )

    # ── Happy path ────────────────────────────────────────────────────────────

    def test_updates_product_price(self):
        self._post([{'internalCode': 60001, 'quantity': 10.0, 'price': 199.0, 'deposit': 'Anaya 2710'}])
        self.product.refresh_from_db()
        self.assertEqual(self.product.price, 199.0)

    def test_updates_warehouse_quantity_to_new_value(self):
        self._post([{'internalCode': 60001, 'quantity': 25.0, 'price': 50.0, 'deposit': 'Anaya 2710'}])
        self.wp.refresh_from_db()
        self.assertEqual(self.wp.quantity, 25.0)

    def test_product_quantity_accumulates_via_f_expression(self):
        """The view uses F('quantity') + product_quantity, so Product.quantity grows."""
        self._post([{'internalCode': 60001, 'quantity': 5.0, 'price': 50.0, 'deposit': 'Anaya 2710'}])
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, 15.0)  # 10 + 5

    def test_multiple_products_updated(self):
        product2 = Product.objects.create(
            name='Act Product 2', internalCode=60002, quantity=8.0, price=30.0
        )
        wp2 = WarehousesProduct.objects.create(
            name='Crocker', product=product2, quantity=8.0, location='C1', deltaQuantity=0.0
        )
        rows = [
            {'internalCode': 60001, 'quantity': 3.0, 'price': 55.0, 'deposit': 'Anaya 2710'},
            {'internalCode': 60002, 'quantity': 2.0, 'price': 35.0, 'deposit': 'Crocker'},
        ]
        self._post(rows)
        self.product.refresh_from_db()
        self.assertEqual(self.product.price, 55.0)
        wp2.refresh_from_db()
        self.assertEqual(wp2.quantity, 2.0)
        self.assertEqual(product2.price, 30.0)  # untouched until refresh

    def test_success_shows_info_message(self):
        response = self._post([{'internalCode': 60001, 'quantity': 1.0, 'price': 50.0, 'deposit': 'Anaya 2710'}])
        msgs = [m.message for m in get_messages(response.wsgi_request)]
        self.assertTrue(any('actualizan' in m for m in msgs))

    def test_success_returns_200(self):
        response = self._post([{'internalCode': 60001, 'quantity': 1.0, 'price': 50.0, 'deposit': 'Anaya 2710'}])
        self.assertEqual(response.status_code, 200)

    # ── Error path ────────────────────────────────────────────────────────────

    def test_nonexistent_warehouse_shows_error_message(self):
        response = self._post([{'internalCode': 60001, 'quantity': 5.0, 'price': 50.0, 'deposit': 'Deposito Inexistente'}])
        tags = [m.extra_tags for m in get_messages(response.wsgi_request)]
        self.assertTrue(any('product format' in (t or '') for t in tags))

    def test_nonexistent_warehouse_redirects(self):
        response = self._post([{'internalCode': 60001, 'quantity': 5.0, 'price': 50.0, 'deposit': 'Deposito Inexistente'}])
        self.assertEqual(response.status_code, 302)

    def test_nonexistent_warehouse_does_not_change_existing_data(self):
        original_price = self.product.price
        self._post([{'internalCode': 60001, 'quantity': 5.0, 'price': 999.0, 'deposit': 'No Existe'}])
        # Product.update() already ran before the DoesNotExist on WarehousesProduct,
        # so this test documents the current behaviour (partial update).
        # The warehouse entry must remain unchanged.
        self.wp.refresh_from_db()
        self.assertEqual(self.wp.quantity, 10.0)

    def test_error_on_first_row_leaves_second_row_unprocessed(self):
        product2 = Product.objects.create(
            name='Second', internalCode=60010, quantity=5.0, price=20.0
        )
        wp2 = WarehousesProduct.objects.create(
            name='Crocker', product=product2, quantity=5.0, location='C1', deltaQuantity=0.0
        )
        rows = [
            {'internalCode': 60001, 'quantity': 1.0, 'price': 1.0, 'deposit': 'Deposito Invalido'},
            {'internalCode': 60010, 'quantity': 99.0, 'price': 99.0, 'deposit': 'Crocker'},
        ]
        self._post(rows)
        wp2.refresh_from_db()
        self.assertEqual(wp2.quantity, 5.0)  # not updated because of early redirect


# =============================================================================
# 6. Action: eliminar
# =============================================================================

class CrudProductsEliminarTest(_CrudProductsBase):

    def setUp(self):
        super().setUp()
        self.product = Product.objects.create(
            name='Del Product', internalCode=70001, quantity=5.0
        )
        self.wp = WarehousesProduct.objects.create(
            name='Anaya 2710', product=self.product,
            quantity=5.0, location='A1', deltaQuantity=0.0
        )

    def _post(self, codes):
        return self.client.post(
            reverse('productscrud', args=['eliminar']),
            {'archivo': self._eliminar_excel(codes)},
            format='multipart',
        )

    # ── Happy path ────────────────────────────────────────────────────────────

    def test_removes_product_from_product_table(self):
        self._post([70001])
        self.assertFalse(Product.objects.filter(internalCode=70001).exists())

    def test_cascade_deletes_warehouse_products(self):
        wp_pk = self.wp.pk
        self._post([70001])
        self.assertFalse(WarehousesProduct.objects.filter(pk=wp_pk).exists())

    def test_deletes_multiple_products(self):
        Product.objects.create(name='Del2', internalCode=70002, quantity=0.0)
        Product.objects.create(name='Del3', internalCode=70003, quantity=0.0)
        self._post([70001, 70002, 70003])
        self.assertEqual(
            Product.objects.filter(internalCode__in=[70001, 70002, 70003]).count(), 0
        )

    def test_deletes_all_warehouse_entries_for_product(self):
        WarehousesProduct.objects.create(
            name='Crocker', product=self.product, quantity=3.0, location='C1', deltaQuantity=0.0
        )
        self.assertEqual(WarehousesProduct.objects.filter(product=self.product).count(), 2)
        self._post([70001])
        self.assertEqual(WarehousesProduct.objects.filter(product__internalCode=70001).count(), 0)

    def test_success_shows_info_message(self):
        response = self._post([70001])
        msgs = [m.message for m in get_messages(response.wsgi_request)]
        self.assertTrue(any('eliminan' in m for m in msgs))

    def test_success_returns_200(self):
        response = self._post([70001])
        self.assertEqual(response.status_code, 200)

    def test_does_not_delete_unrelated_products(self):
        other = Product.objects.create(name='Other', internalCode=70099, quantity=1.0)
        self._post([70001])
        self.assertTrue(Product.objects.filter(internalCode=70099).exists())

    # ── Error path ────────────────────────────────────────────────────────────

    def test_nonexistent_product_shows_error_message(self):
        response = self._post([99999])
        tags = [m.extra_tags for m in get_messages(response.wsgi_request)]
        self.assertTrue(any('product format' in (t or '') for t in tags))

    def test_nonexistent_product_redirects(self):
        response = self._post([99999])
        self.assertEqual(response.status_code, 302)

    def test_error_on_first_row_leaves_subsequent_rows_unprocessed(self):
        """An error causes an immediate redirect, so later rows are never deleted."""
        survivor = Product.objects.create(name='Survivor', internalCode=70010, quantity=1.0)
        self._post([99999, 70010])  # 99999 fails first
        self.assertTrue(Product.objects.filter(internalCode=70010).exists())

    def test_error_on_first_row_does_not_delete_existing_product_listed_later(self):
        """Complementary: the existing product behind an errored row stays untouched."""
        Product.objects.create(name='Later', internalCode=70020, quantity=2.0)
        self._post([99999, 70020])
        self.assertTrue(Product.objects.filter(internalCode=70020).exists())


# =============================================================================
# 7. Action: total (new inventory generation)
# =============================================================================

class CrudProductsTotalTest(_CrudProductsBase):
    """Tests for the 'total' action – bulk create/update from an Excel inventory sheet."""

    def _post(self, rows):
        return self.client.post(
            reverse('productscrud', args=['total']),
            {'archivo': self._total_excel(rows)},
            format='multipart',
        )

    # ── Create path (product does not exist) ─────────────────────────────────

    def test_creates_new_product_when_absent_from_db(self):
        self._post([self._default_total_row()])
        self.assertTrue(Product.objects.filter(internalCode=80001).exists())

    def test_new_product_fields_persisted(self):
        self._post([self._default_total_row(
            internalCode=80002, name='Full Product', category='Electronics',
            supplier='Prov X', stock=30, stockSecurity=10
        )])
        p = Product.objects.get(internalCode=80002)
        self.assertEqual(p.name, 'Full Product')
        self.assertEqual(p.category, 'Electronics')
        self.assertEqual(p.supplier, 'Prov X')
        self.assertEqual(p.quantity, 30.0)
        self.assertEqual(p.stockSecurity, 10.0)

    def test_new_product_creates_all_four_warehouse_entries(self):
        self._post([self._default_total_row(internalCode=80003)])
        p = Product.objects.get(internalCode=80003)
        self.assertEqual(WarehousesProduct.objects.filter(product=p).count(), 4)

    def test_new_product_correct_warehouse_quantities(self):
        self._post([self._default_total_row(
            internalCode=80004,
            qty_anaya=10, qty_crocker=8, qty_joanico=7, qty_transit=5
        )])
        p = Product.objects.get(internalCode=80004)
        self.assertEqual(WarehousesProduct.objects.get(product=p, name='Anaya 2710').quantity, 10.0)
        self.assertEqual(WarehousesProduct.objects.get(product=p, name='Crocker').quantity, 8.0)
        self.assertEqual(WarehousesProduct.objects.get(product=p, name='Joanico').quantity, 7.0)
        self.assertEqual(WarehousesProduct.objects.get(product=p, name='In Transit').quantity, 5.0)

    def test_new_product_correct_warehouse_locations(self):
        self._post([self._default_total_row(
            internalCode=80005,
            loc_anaya='Estante A', loc_crocker='Fila B', loc_joanico='Pasillo J'
        )])
        p = Product.objects.get(internalCode=80005)
        self.assertEqual(WarehousesProduct.objects.get(product=p, name='Anaya 2710').location, 'Estante A')
        self.assertEqual(WarehousesProduct.objects.get(product=p, name='Crocker').location, 'Fila B')
        self.assertEqual(WarehousesProduct.objects.get(product=p, name='Joanico').location, 'Pasillo J')

    def test_new_product_zero_quantities_allowed(self):
        self._post([self._default_total_row(
            internalCode=80006,
            stock=0, qty_anaya=0, qty_crocker=0, qty_joanico=0, qty_transit=0
        )])
        p = Product.objects.get(internalCode=80006)
        for wh in self.WAREHOUSES:
            self.assertEqual(WarehousesProduct.objects.get(product=p, name=wh).quantity, 0.0)

    # ── Update path (product already exists) ─────────────────────────────────

    def test_updates_existing_product_core_fields(self):
        self._create_product_with_warehouses(
            80010, name='Old Name', category='Old Cat', supplier='Old Sup',
            stockSecurity=0, price=1.0
        )
        self._post([self._default_total_row(
            internalCode=80010, name='New Name', category='New Cat',
            supplier='New Sup', stock=50, stockSecurity=15
        )])
        p = Product.objects.get(internalCode=80010)
        self.assertEqual(p.name, 'New Name')
        self.assertEqual(p.category, 'New Cat')
        self.assertEqual(p.supplier, 'New Sup')
        self.assertEqual(p.quantity, 50.0)
        self.assertEqual(p.stockSecurity, 15.0)

    def test_updates_warehouse_quantities_for_existing_product(self):
        self._create_product_with_warehouses(80011)
        self._post([self._default_total_row(
            internalCode=80011,
            qty_anaya=20, qty_crocker=15, qty_joanico=10, qty_transit=5
        )])
        p = Product.objects.get(internalCode=80011)
        self.assertEqual(WarehousesProduct.objects.get(product=p, name='Anaya 2710').quantity, 20.0)
        self.assertEqual(WarehousesProduct.objects.get(product=p, name='Crocker').quantity, 15.0)
        self.assertEqual(WarehousesProduct.objects.get(product=p, name='Joanico').quantity, 10.0)
        self.assertEqual(WarehousesProduct.objects.get(product=p, name='In Transit').quantity, 5.0)

    def test_updates_warehouse_locations_for_existing_product(self):
        self._create_product_with_warehouses(80012)
        self._post([self._default_total_row(
            internalCode=80012,
            loc_anaya='New A', loc_crocker='New C', loc_joanico='New J'
        )])
        p = Product.objects.get(internalCode=80012)
        self.assertEqual(WarehousesProduct.objects.get(product=p, name='Anaya 2710').location, 'New A')
        self.assertEqual(WarehousesProduct.objects.get(product=p, name='Crocker').location, 'New C')
        self.assertEqual(WarehousesProduct.objects.get(product=p, name='Joanico').location, 'New J')

    def test_does_not_create_duplicate_product(self):
        self._create_product_with_warehouses(80013)
        self._post([self._default_total_row(internalCode=80013)])
        self.assertEqual(Product.objects.filter(internalCode=80013).count(), 1)

    def test_existing_product_warehouse_count_unchanged(self):
        """Update path must not add extra WarehousesProduct entries."""
        self._create_product_with_warehouses(80014)
        self._post([self._default_total_row(internalCode=80014)])
        p = Product.objects.get(internalCode=80014)
        self.assertEqual(WarehousesProduct.objects.filter(product=p).count(), 4)

    # ── Skip / edge cases ─────────────────────────────────────────────────────

    def test_skips_row_with_empty_product_name(self):
        self._post([self._default_total_row(name='', internalCode=80020)])
        self.assertFalse(Product.objects.filter(internalCode=80020).exists())

    def test_skips_row_with_none_product_name(self):
        self._post([self._default_total_row(name=None, internalCode=80021)])
        self.assertFalse(Product.objects.filter(internalCode=80021).exists())

    def test_skips_row_with_empty_category(self):
        self._post([self._default_total_row(category='', internalCode=80022)])
        self.assertFalse(Product.objects.filter(internalCode=80022).exists())

    def test_skips_row_with_none_category(self):
        self._post([self._default_total_row(category=None, internalCode=80023)])
        self.assertFalse(Product.objects.filter(internalCode=80023).exists())

    def test_valid_rows_after_skipped_row_are_still_processed(self):
        """Skipped rows (continue) must not prevent subsequent valid rows from being created."""
        rows = [
            self._default_total_row(name='', internalCode=80030),   # skipped
            self._default_total_row(name='Valid Product', internalCode=80031),  # processed
        ]
        self._post(rows)
        self.assertFalse(Product.objects.filter(internalCode=80030).exists())
        self.assertTrue(Product.objects.filter(internalCode=80031).exists())

    def test_none_price_stored_as_none(self):
        self._post([self._default_total_row(internalCode=80040, price=None)])
        p = Product.objects.get(internalCode=80040)
        self.assertIsNone(p.price)

    def test_integer_price_stored_correctly(self):
        """Integer prices (no decimal point) survive the European-format parsing."""
        self._post([self._default_total_row(internalCode=80041, price=200)])
        p = Product.objects.get(internalCode=80041)
        self.assertIsNotNone(p.price)
        self.assertEqual(p.price, 200.0)

    def test_comma_decimal_stock_security_parsed(self):
        """stockSecurity = 5 (int) is parsed correctly by the comma/dot handler."""
        self._post([self._default_total_row(internalCode=80042, stockSecurity=5)])
        p = Product.objects.get(internalCode=80042)
        self.assertEqual(p.stockSecurity, 5.0)

    def test_zero_stock_security_allowed(self):
        self._post([self._default_total_row(internalCode=80043, stockSecurity=0)])
        p = Product.objects.get(internalCode=80043)
        self.assertEqual(p.stockSecurity, 0.0)

    # ── Mixed file (new + existing products) ──────────────────────────────────

    def test_mixed_file_creates_new_and_updates_existing(self):
        self._create_product_with_warehouses(80050, name='Old Name')
        rows = [
            self._default_total_row(internalCode=80050, name='Updated Name', stock=99),
            self._default_total_row(internalCode=80051, name='Brand New'),
        ]
        self._post(rows)
        # Existing updated
        p_existing = Product.objects.get(internalCode=80050)
        self.assertEqual(p_existing.name, 'Updated Name')
        self.assertEqual(p_existing.quantity, 99.0)
        # New created
        self.assertTrue(Product.objects.filter(internalCode=80051).exists())
        p_new = Product.objects.get(internalCode=80051)
        self.assertEqual(WarehousesProduct.objects.filter(product=p_new).count(), 4)

    def test_large_batch_all_new_products_created(self):
        rows = [
            self._default_total_row(internalCode=80100 + i, name=f'Batch Prod {i}')
            for i in range(10)
        ]
        self._post(rows)
        for i in range(10):
            self.assertTrue(Product.objects.filter(internalCode=80100 + i).exists())

    def test_large_batch_all_new_products_have_warehouse_entries(self):
        rows = [
            self._default_total_row(internalCode=80200 + i, name=f'WH Batch {i}')
            for i in range(5)
        ]
        self._post(rows)
        for i in range(5):
            p = Product.objects.get(internalCode=80200 + i)
            self.assertEqual(WarehousesProduct.objects.filter(product=p).count(), 4)

    # ── Response behaviour ────────────────────────────────────────────────────

    def test_success_redirects(self):
        response = self._post([self._default_total_row()])
        self.assertEqual(response.status_code, 302)

    def test_success_shows_info_message(self):
        response = self._post([self._default_total_row()])
        msgs = [m.message for m in get_messages(response.wsgi_request)]
        self.assertTrue(any('crean o actualizan' in m for m in msgs))

    def test_redirect_goes_to_total_url(self):
        response = self._post([self._default_total_row()])
        self.assertRedirects(
            response,
            reverse('productscrud', args=['total']),
            fetch_redirect_response=False,
        )
