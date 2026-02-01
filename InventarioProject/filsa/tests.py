from django.test import TestCase, Client
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
            motivoEgreso="Ventas",
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
#        self.client.login(username='testuser', password='testpass')
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
        response = self.client.post(reverse('inbound'), data, follow=True)
        self.assertIn(response.status_code, [302, 200])  # Success on form submission
        self.assertGreater(Tasks.objects.count(), initial_tasks)
        self.assertGreater(StockMovements.objects.count(), initial_movements)
        self.warehouse.refresh_from_db()
        # Quantity in warehouse is updated only when inbound is confirmed
        self.assertEqual(self.warehouse.quantity, 0.0)


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
        response = self.client.post(reverse('outboundorder'), data, follow=True)
        self.assertIn(response.status_code, [200, 302])
        self.assertGreater(Tasks.objects.count(), initial_tasks)
        self.assertGreater(StockMovements.objects.count(), initial_movements)
        self.warehouse.refresh_from_db()
        # Quantity in warehouse is updated only when outbound is delivered/confirmed
        self.assertEqual(self.warehouse.quantity, 20)


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
         #   'dest_warehouse': self.dest_warehouse.name,
            'extra_field_count': 1,
            'department': 'Ventas',
            'date': '2023-01-01',
            'issuer': self.user.id,
            'receptor': self.user.id,
        }

        initial_tasks = Tasks.objects.count()
        initial_movements = StockMovements.objects.count()
        response = self.client.post(reverse('transfer'), data, follow=True)
        self.assertIn(response.status_code, [200, 302])
        self.assertGreater(Tasks.objects.count(), initial_tasks)
        self.assertGreater(StockMovements.objects.count(), initial_movements)
        self.source_warehouse.refresh_from_db()
        self.dest_warehouse.refresh_from_db()
        # Quantities are updated only when transfer is confirmed (transferReceptionView)
        self.assertEqual(self.source_warehouse.quantity, 20)
        self.assertEqual(self.dest_warehouse.quantity, 10)

