from django.core.management.base import BaseCommand, CommandError
from filsa.models import CustomUser, StockMovements, DiffProducts, Product, WarehousesProduct, Tasks, Cotization
from django.contrib.auth.models import Group
import csv
from datetime import datetime
import re
import math

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


      #  customer = 'UTE'
      #  numberOfProducts = 5
      #  registered_date = datetime.now().date()

        Cotization.objects.create()

        warehouses_list = ['Anaya 2710' , 'Crocker 2652' , 'Juanico' ,'Taller', 'En Transito']

        customer = 'UTE'
        
        # warehouse_object = []
        # for i in range(0,len(warehouses_list)):
        #     warehouses_model = Warehouses()
        #     warehouses_model.name = warehouses_list[i]
        #     warehouse_object.append(warehouses_model)

        # Warehouses.objects.bulk_create(warehouse_object)


        #users_file = './usuariosFilsa.txt' 
        #products_file = './productosFilsa.txt' 
        users_file = "C:/Users/nicol/Inventario/InventarioProject/filsa/management/commands/usuariosFilsa.txt"
        products_file = "C:/Users/nicol/Inventario/InventarioProject/filsa/management/commands/productosFilsa.txt"
        new_products_file = "C:/Users/nicol/Inventario/InventarioProject/filsa/management/filsa_out6.csv"
        #f = open(users_file, "r")
        #reader = f.read()
        #users_lines = list(reader)
        
        with open(users_file, 'r') as file:
        #     #print(file.readlines())
            users_lines = file.readlines()
        # # Archivo: Nombre,Correo,Contraseña, Deparamento,Rol
            #users_obj = []
            superuser = CustomUser.objects.create_superuser(username = 'filsacompany' , email='operaciones@filsa.com.uy', password='sitioweb_2024')
            for line in users_lines[1:]:
                
                user_model = CustomUser()
                # print('user line is ', line)
                line = line.split(',')
                print('lines is:',line)
                nombre_usuario = line[0]
                correo = line[2]
                password = line[1]
                departamento = line[3]
                rol = line[4]
                # print('username', line[0])
                # user_model.username = line[0]
                # print('email', line[2])
                # user_model.email = line[2]
                # user_model.password = line[1]
                # user_model.departamento = line[3]
                # user_model.role = line[4]
                userobj = CustomUser.objects.create_user(username= nombre_usuario, password=password, email=correo, departamento=departamento,role=rol)
               # userobj.save()
                user_group ,  created = Group.objects.get_or_create(name=rol) 
                user_group.user_set.add(userobj)
                
               # users_obj.append(user_model)


            #CustomUser.objects.bulk_create(users_obj)
        #f = open(products_file, "r")
        #reader = f.read()
        #lines = list(reader)
        
        objects = []
        with open(new_products_file,  newline='',  encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            i = 0
            dd = []
            for row in reader:
                if ((row['Producto'] == '')  or (row['Producto'] == None) or (row['Codigo'] == '')):
                    continue
                product_model = Product()
                #warehouse_product_model = WarehousesProduct()
                i +=1 
                # Create an empty instance of your model
                
                product_model.name= row['Producto'].strip().lower().title()

                product_model.barcode= row['CodigoOrigen']
                product_model.internalCode= row['Codigo']
                
                print('price list is:', row["PRECIO DE LISTA USD"])

                if (row["PRECIO DE LISTA USD"] == '') or (row["PRECIO DE LISTA USD"] == 'USD -')  or (row["PRECIO DE LISTA USD"].strip() == '-'):
                    price = 0
                    product_model.price= price
                else: 
                    try: 
                        price = row['PRECIO DE LISTA USD'].replace(',','.').strip().replace('USD','')
                        price =  price.replace('.','', price.count('.') -1)
                        print('new price is:', price)
                        if price == '-' or price == ' -':
                            price = 0
                        else:
                            product_model.price= price
                        if '-' in price:
                            dd.append(price)
                    except Exception as e:
                        print(e)
                        print('i is', i)
                        print('precio con error es:', row["PRECIO DE LISTA USD"])
                        price = 0
                        product_model.price= price
                

                product_model.deltaQuantity= 0
                if row['StockActual'] == '':
                    quantity  = 0
                else:
                    quantity = row['StockActual'].replace(',','.')

                product_model.quantity= quantity
                product_model.category= row['Categoria'].lower().title()
                #product_model.location= row['Ubicacion']
                product_model.supplier= row['Proveedor'].lower().title()
                #print('warehouse is ', warehouse_name)
                # print('i is',i)
                # print('stockSecurity is', row['StockSeguridad'])
                
                product_model.deltaQuantity= 0
                if row['StockSeguridad'] == '':
                    row['StockSeguridad'] = 0

                product_model.stockSecurity= row['StockSeguridad']
                product_model.inTransit = False

                print('product name is')
                print(product_model.name)
                
                objects.append(product_model)
            
            print('weird list is:', dd)

            Product.objects.bulk_create(objects, ignore_conflicts=True)


        objects = []
        with open(new_products_file,  newline='', encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            i = 0
            for row in reader:
                #product_model = Product()
                if row['Producto'] == '' or row['Producto'] == None:
                    print('product {} with code {} is None or empty'.format(row['Producto'], row['Codigo']))
                    continue
                
                i +=1  
                anaya_quantity = row['STOCK ANAYA 2710']
                crocker_quantity = row['STOCK CROCKER']
                juanico_quantity = row['STOCK JUANICO']
                
                #try:

                try:
                    #print('producto antes del get is {} with internalCode {}'.format(row['Producto'], row['internalCode']))
                    product_name = row['Producto'].strip().lower().title()
                    internalCode = row['Codigo']
                    product = Product.objects.get(internalCode= internalCode)
                    
                    if anaya_quantity != '':
                        # print('entra en anaya with quantity', anaya_quantity)
                        warehouse_product_model_anaya = WarehousesProduct()
                        warehouse_product_model_anaya.name = 'Anaya 2710'
                        #product_model.name= row['Producto']
                        #print('product in Anaya is', row['Producto'])
                        warehouse_product_model_anaya.product = Product.objects.get(product_id=product.product_id)
                       
                       #warehouse_product_model.product_id = product.product_id
                        
                        warehouse_product_model_anaya.quantity = anaya_quantity.replace(',','')
                        warehouse_product_model_anaya.location = row['Ubicación Anaya']
                        warehouse_product_model_anaya.deltaQuantity = 0
                        objects.append(warehouse_product_model_anaya)

                    if crocker_quantity != '':
                        # print('entra en crocker with quantity', crocker_quantity)
                        warehouse_product_model_crocker = WarehousesProduct()
                        warehouse_product_model_crocker.name = 'Crocker'
                        #print('product in Crocker is', row['Producto'])
                        warehouse_product_model_crocker.product =  Product.objects.get(product_id=product.product_id) #  product # Product.objects.get(name=row['Producto'])
                        warehouse_product_model_crocker.quantity = crocker_quantity.replace(',','')
                        warehouse_product_model_crocker.location = row['Ubicación Crocker']
                        warehouse_product_model_crocker.deltaQuantity = 0
                        objects.append(warehouse_product_model_crocker)

                    if juanico_quantity != '':
                        # print('entra en juanico with quantity', juanico_quantity)
                        warehouse_product_model_juanico = WarehousesProduct()
                        warehouse_product_model_juanico.name = 'Juanico'
                        #print('product in Juanico is', row['Producto'])
                        warehouse_product_model_juanico.product = Product.objects.get(product_id=product.product_id)    # product #   Product.objects.get(name=row['Producto'])
                        warehouse_product_model_juanico.quantity = juanico_quantity.replace(',','')
                        warehouse_product_model_juanico.location = row['Ubicación Juanico']
                        warehouse_product_model_juanico.deltaQuantity = 0
                        objects.append(warehouse_product_model_juanico)

                    if ((anaya_quantity == "") and (crocker_quantity == "") and (juanico_quantity == "")):
                        warehouse_product_model_without_stock = WarehousesProduct()
                        warehouse_product_model_without_stock.product = Product.objects.get(product_id=product.product_id)
                        warehouse_product_model_without_stock.deltaQuantity = 0
                        warehouse_product_model_without_stock.quantity = 0
                        warehouse_product_model_without_stock.name = 'No Stock'
                        objects.append(warehouse_product_model_without_stock)

                except Exception as e:
                    print(e)
                    print('producto no encontrado es {} con codigo {}'.format(row['Producto'], row['Codigo']))
                    #if row['internalCode'] != '':
                    #    print('producto no encontrado tiene codigo  {}'.format(row['internalCode']))

                #objects.append(warehouse_product_model)

            WarehousesProduct.objects.bulk_create(objects)
            
    # Populate the fields of the model based on the record line of your file
#    obj.field1 = line[0] # The first column
#    obj.field2 = line[1] # The second column
    # Add the model to the list of objects
 #   objects.append(obj)

# Save all objects simultaniously, instead of saving for each line
