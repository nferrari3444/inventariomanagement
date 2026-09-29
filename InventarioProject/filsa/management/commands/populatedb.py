from django.core.management.base import BaseCommand, CommandError
from filsa.models import CustomUser, StockMovements, DiffProducts, Product, WarehousesProduct, Tasks, Cotization
from django.contrib.auth.models import Group
from django.db import transaction
import csv
from datetime import datetime
import re
import math
import os

dirname = os.path.dirname(__file__)

 
class Command(BaseCommand):
    help = 'import data'

    def add_arguments(self, parser):
        pass
        # this is optional so that your management command can just accept the
        # path of the csv instead of a hardcoded path
        # parser.add_argument(
        #     'csv_file',
        #     help='path to csv file',
        #     type=str)

    def handle(self, *args, **options):
        self._load_users(os.path.join(dirname, 'usuariosFilsa.txt'))

    @transaction.atomic
    def _load_users(self, users_file):
        # Archivo: Nombre,Contrasenia,Correo,Deparamento,Rol
        # Idempotente: los usuarios cuyo email ya existe se saltean.
        created = skipped = 0
        with open(users_file, newline='', encoding='utf-8') as file:
            for row in csv.DictReader(file):
                row = {key.strip(): (value or '').strip() for key, value in row.items()}
                email = row['Correo'].lower()
                role = row['Rol']

                if CustomUser.objects.filter(email=email).exists():
                    skipped += 1
                    continue

                user = CustomUser.objects.create_user(
                    email=email,
                    password=row['Contrasenia'],
                    username=row['Nombre'],
                    departamento=row['Deparamento'],
                    role=role,
                )
                group, _ = Group.objects.get_or_create(name=role)
                group.user_set.add(user)
                created += 1

        self.stdout.write(self.style.SUCCESS(
            f'Usuarios: {created} creados, {skipped} ya existían.'
        ))
        #f = open(products_file, "r")
        #reader = f.read()
        #lines = list(reader)
        # Se borran las siguientes lineas porque los productos se dan de alta con la funcionalidad
        # nueva de excel. Se borra lineas desde la 99-245

        # objects = []
        # with open(new_products_file,  newline='',  encoding="utf-8") as csvfile:
        #     reader = csv.DictReader(csvfile)
        #     i = 0
        #     dd = []
        #     for row in reader:
        #         if ((row['Producto'] == '')  or (row['Producto'] == None) or (row['Codigo'] == '')):
        #             continue
        #         product_model = Product()
        #         #warehouse_product_model = WarehousesProduct()
        #         i +=1 
        #         # Create an empty instance of your model
                
        #         product_model.name= row['Producto'].strip().lower().title()

        #         product_model.barcode= row['CodigoOrigen']
        #         product_model.internalCode= row['Codigo']
                
        #         print('price list is:', row["PRECIO DE LISTA USD"])

        #         if (row["PRECIO DE LISTA USD"] == '') or (row["PRECIO DE LISTA USD"] == 'USD -')  or (row["PRECIO DE LISTA USD"].strip() == '-'):
        #             price = 0
        #             product_model.price= price
        #         else: 
        #             try: 
        #                 price = row['PRECIO DE LISTA USD'].replace(',','.').strip().replace('USD','')
        #                 price =  price.replace('.','', price.count('.') -1)
        #                 print('new price is:', price)
        #                 if price == '-' or price == ' -':
        #                     price = 0
        #                 else:
        #                     product_model.price= price
        #                 if '-' in price:
        #                     dd.append(price)
        #             except Exception as e:
        #                 print(e)
        #                 print('i is', i)
        #                 print('precio con error es:', row["PRECIO DE LISTA USD"])
        #                 price = 0
        #                 product_model.price= price
                

        #         product_model.deltaQuantity= 0
        #         if row['StockActual'] == '':
        #             quantity  = 0
        #         else:
        #             quantity = row['StockActual'].replace(',','.')

        #         product_model.quantity= quantity
        #         product_model.category= row['Categoria'].lower().title()
        #         #product_model.location= row['Ubicacion']
        #         product_model.supplier= row['Proveedor'].lower().title()
        #         #print('warehouse is ', warehouse_name)
        #         # print('i is',i)
        #         # print('stockSecurity is', row['StockSeguridad'])
                
        #         product_model.deltaQuantity= 0
        #         if row['StockSeguridad'] == '':
        #             row['StockSeguridad'] = 0

        #         product_model.stockSecurity= row['StockSeguridad']
        #         product_model.inTransit = False

        #         print('product name is')
        #         print(product_model.name)
                
        #         objects.append(product_model)
            
        #     print('weird list is:', dd)

        #     Product.objects.bulk_create(objects, ignore_conflicts=True)


        # objects = []
        # with open(new_products_file,  newline='', encoding="utf-8") as csvfile:
        #     reader = csv.DictReader(csvfile)
        #     i = 0
        #     for row in reader:
        #         #product_model = Product()
        #         if row['Producto'] == '' or row['Producto'] == None:
        #             print('product {} with code {} is None or empty'.format(row['Producto'], row['Codigo']))
        #             continue
                
        #         i +=1  
        #         anaya_quantity = row['STOCK ANAYA 2710']
        #         crocker_quantity = row['STOCK CROCKER']
        #         juanico_quantity = row['STOCK JUANICO']
                
        #         #try:

        #         try:
        #             #print('producto antes del get is {} with internalCode {}'.format(row['Producto'], row['internalCode']))
        #             product_name = row['Producto'].strip().lower().title()
        #             internalCode = row['Codigo']
        #             product = Product.objects.get(internalCode= internalCode)
                    
        #             if anaya_quantity != '':
        #                 # print('entra en anaya with quantity', anaya_quantity)
        #                 warehouse_product_model_anaya = WarehousesProduct()
        #                 warehouse_product_model_anaya.name = 'Anaya 2710'
        #                 #product_model.name= row['Producto']
        #                 #print('product in Anaya is', row['Producto'])
        #                 warehouse_product_model_anaya.product = Product.objects.get(product_id=product.product_id)
                       
        #                #warehouse_product_model.product_id = product.product_id
                        
        #                 warehouse_product_model_anaya.quantity = anaya_quantity.replace(',','')
        #                 warehouse_product_model_anaya.location = row['Ubicación Anaya']
        #                 warehouse_product_model_anaya.deltaQuantity = 0
        #                 objects.append(warehouse_product_model_anaya)

        #             if crocker_quantity != '':
        #                 # print('entra en crocker with quantity', crocker_quantity)
        #                 warehouse_product_model_crocker = WarehousesProduct()
        #                 warehouse_product_model_crocker.name = 'Crocker'
        #                 #print('product in Crocker is', row['Producto'])
        #                 warehouse_product_model_crocker.product =  Product.objects.get(product_id=product.product_id) #  product # Product.objects.get(name=row['Producto'])
        #                 warehouse_product_model_crocker.quantity = crocker_quantity.replace(',','')
        #                 warehouse_product_model_crocker.location = row['Ubicación Crocker']
        #                 warehouse_product_model_crocker.deltaQuantity = 0
        #                 objects.append(warehouse_product_model_crocker)

        #             if juanico_quantity != '':
        #                 # print('entra en juanico with quantity', juanico_quantity)
        #                 warehouse_product_model_juanico = WarehousesProduct()
        #                 warehouse_product_model_juanico.name = 'Juanico'
        #                 #print('product in Juanico is', row['Producto'])
        #                 warehouse_product_model_juanico.product = Product.objects.get(product_id=product.product_id)    # product #   Product.objects.get(name=row['Producto'])
        #                 warehouse_product_model_juanico.quantity = juanico_quantity.replace(',','')
        #                 warehouse_product_model_juanico.location = row['Ubicación Juanico']
        #                 warehouse_product_model_juanico.deltaQuantity = 0
        #                 objects.append(warehouse_product_model_juanico)

        #             if ((anaya_quantity == "") and (crocker_quantity == "") and (juanico_quantity == "")):
        #                 warehouse_product_model_without_stock = WarehousesProduct()
        #                 warehouse_product_model_without_stock.product = Product.objects.get(product_id=product.product_id)
        #                 warehouse_product_model_without_stock.deltaQuantity = 0
        #                 warehouse_product_model_without_stock.quantity = 0
        #                 warehouse_product_model_without_stock.name = 'No Stock'
        #                 objects.append(warehouse_product_model_without_stock)

        #         except Exception as e:
        #             print(e)
        #             print('producto no encontrado es {} con codigo {}'.format(row['Producto'], row['Codigo']))
        #             #if row['internalCode'] != '':
        #             #    print('producto no encontrado tiene codigo  {}'.format(row['internalCode']))

        #         #objects.append(warehouse_product_model)

        #     WarehousesProduct.objects.bulk_create(objects)
            
    # Populate the fields of the model based on the record line of your file
#    obj.field1 = line[0] # The first column
#    obj.field2 = line[1] # The second column
    # Add the model to the list of objects
 #   objects.append(obj)

# Save all objects simultaniously, instead of saving for each line
