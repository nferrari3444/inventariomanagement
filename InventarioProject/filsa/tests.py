# from django.test import TestCase
# from django.urls import reverse
# from django.contrib.auth import get_user_model
# from .models import Product, WarehousesProduct, Tasks, StockMovements, DiffProducts, Cotization
# from .views import update_product_warehouse, create_products_warehouse
# from functools import reduce
# from django.db.models import Q

# User = get_user_model()


# # import psycopg2

# # try: 
# #     conn = psycopg2.connect(
# #         host="127.0.0.1",
# #         database="filsadb_dev",
# #         user="filsa_dev",
# #         password="Filsa.2024",
# #         port=5432)
# #     print("Database connection successful")
# # except Exception as e:
# #     print(f"Database connection failed: {e}")
# class ProductModelTest(TestCase):
#     def setUp(self):
#         self.product = Product.objects.create(
#             name="Test Product",
#             barcode="123456789",
#             internalCode=12345,
#             quantity=10.0,
#             category="Test Category",
#             supplier="Test Supplier",
#             stockSecurity=5,
#             price=100.0,
#             currency="USD"
#         )

#     def test_product_creation(self):
#         self.assertEqual(self.product.name, "Test Product")
#         self.assertEqual(self.product.barcode, "123456789")
#         self.assertEqual(self.product.quantity, 10.0)

#     def test_product_str(self):
#         self.assertEqual(str(self.product), "Test Product")

# class WarehousesProductModelTest(TestCase):
#     def setUp(self):
#         self.product = Product.objects.create(
#             name="Warehouse Product",
#             barcode="987654321",
#             internalCode=54321,
#             quantity=20.0
#         )
#         self.warehouse_product = WarehousesProduct.objects.create(
#             name="Main Warehouse",
#             product=self.product,
#             quantity=15.0,
#             location="Aisle 1",
#             deltaQuantity=0.0
#         )

#     def test_warehouse_product_creation(self):
#         self.assertEqual(self.warehouse_product.name, "Main Warehouse")
#         self.assertEqual(self.warehouse_product.product.name, "Warehouse Product")
#         self.assertEqual(self.warehouse_product.quantity, 15.0)

#     def test_warehouse_product_str(self):
#         self.assertEqual(str(self.warehouse_product), "Main Warehouse")

#     def test_delete_creates_stock_movement(self):
#         # Deleting WarehousesProduct should create a StockMovements entry
#         initial_count = StockMovements.objects.count()
#         self.warehouse_product.delete()
#         final_count = StockMovements.objects.count()
#         self.assertEqual(final_count, initial_count + 1)
#         movement = StockMovements.objects.last()
#         self.assertIn("deleted!", movement.actionType)

#     def test_update_product_warehouse(self):
#         # Create additional warehouse products for testing update
#         wp_a = WarehousesProduct.objects.create(
#             name="Deposito A",
#             product=self.product,
#             quantity=10.0,
#             location="Location A",
#             deltaQuantity=0.0
#         )
#         wp_b = WarehousesProduct.objects.create(
#             name="Deposito B",
#             product=self.product,
#             quantity=10.0,
#             location="Location B",
#             deltaQuantity=0.0
#         )

#         # Prepare data for update
#         deposits = ['Deposito A', 'Deposito B']
#         product_code = self.product.internalCode
#         product_warehouse_quantities = [
#             ('Deposito A', 25.0, 'Updated Location A'),
#             ('Deposito B', 30.0, 'Updated Location B')
#         ]

#         # Call the function
#         results = update_product_warehouse(deposits, product_code, product_warehouse_quantities)

#         # Verify updates
#         self.assertEqual(len(results), 2)
#         wp_a.refresh_from_db()
#         wp_b.refresh_from_db()
#         self.assertEqual(wp_a.quantity, 25.0)
#         self.assertEqual(wp_a.location, 'Updated Location A')
#         self.assertEqual(wp_b.quantity, 30.0)
#         self.assertEqual(wp_b.location, 'Updated Location B')

#     def test_create_products_warehouse(self):
#         # Use a different product for create test
#         new_product = Product.objects.create(
#             name="New Test Product",
#             barcode="NEW123",
#             internalCode=88888,
#             quantity=50.0
#         )

#         # Prepare data for create
#         deposits = ['New Deposito X', 'New Deposito Y']
#         product_code = new_product.internalCode
#         product_warehouse_quantities = [
#             ('New Deposito X', 15.0, 'Location X'),
#             ('New Deposito Y', 20.0, 'Location Y')
#         ]

#         initial_count = WarehousesProduct.objects.filter(product=new_product).count()
#         self.assertEqual(initial_count, 0)

#         # Call the function
#         create_products_warehouse(deposits, product_code, product_warehouse_quantities)

#         # Verify creations
#         final_count = WarehousesProduct.objects.filter(product=new_product).count()
#         self.assertEqual(final_count, 2)

#         wp_x = WarehousesProduct.objects.get(product=new_product, name='New Deposito X')
#         wp_y = WarehousesProduct.objects.get(product=new_product, name='New Deposito Y')

#         self.assertEqual(wp_x.quantity, 15.0)
#         self.assertEqual(wp_x.location, 'Location X')
#         self.assertEqual(wp_y.quantity, 20.0)
#         self.assertEqual(wp_y.location, 'Location Y')

# class TasksModelTest(TestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(
#             username="testuser",
#             email="test@example.com",
#             password="testpass123"
#         )
#         self.product = Product.objects.create(
#             name="Task Product",
#             barcode="111111111",
#             internalCode=11111
#         )
#         self.warehouse_product = WarehousesProduct.objects.create(
#             name="Task Warehouse",
#             product=self.product
#         )
#         self.task = Tasks.objects.create(
#             receptor=self.user,
#             issuer=self.user,
#             department="Ventas",
#             date="2023-01-01",
#             motivoIngreso="Compra en Plaza",
#             motivoEgreso="Ventas",
#             warehouseProduct=self.warehouse_product,
#             actionType="Inbound"
#         )

#     def test_task_creation(self):
#         self.assertEqual(self.task.status, "Pending")
#         self.assertEqual(self.task.actionType, "Inbound")
#         self.assertEqual(self.task.receptor.username, "testuser")

# class HomeViewTest(TestCase):
#     def test_home_view_status_code(self):
#         response = self.client.get(reverse('home'))
#         self.assertEqual(response.status_code, 200)

#     def test_home_view_template(self):
#         response = self.client.get(reverse('home'))
#         self.assertTemplateUsed(response, 'home.html')
