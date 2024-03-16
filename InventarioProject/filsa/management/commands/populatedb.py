from django.core.management.base import BaseCommand, CommandError
from filsa.models import CustomUser, StockMovements, DiffProducts, Product, WarehousesProduct, Tasks, Cotization
from django.contrib.auth.models import Group
import csv
from datetime import datetime

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
        new_products_file = "C:/Users/nicol/Inventario/InventarioProject/filsa/management/ProdsFilsa.csv"
        #f = open(users_file, "r")
        #reader = f.read()
        #users_lines = list(reader)
        
        with open(users_file) as file:
        #     #print(file.readlines())
            users_lines = file.readlines()
        # # Archivo: Nombre,Correo,Contraseña, Deparamento,Rol
            users_obj = []
            superuser = CustomUser.objects.create_superuser(username = 'filsacompany' , email='operaciones@filsa.com.uy', password='sitioweb_2024')
            for line in users_lines[1:]:
                
                user_model = CustomUser()
                # print('user line is ', line)
                line = line.split(',')
                print(line)
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
                
             #   users_obj.append(user_model)


     #   CustomUser.objects.bulk_create(users_obj)




        #f = open(products_file, "r")
        #reader = f.read()
        #lines = list(reader)
        
        objects = []
        with open(new_products_file,  newline='', encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            i = 0
            for row in reader:
                product_model = Product()
                #warehouse_product_model = WarehousesProduct()
                i +=1 
                # Create an empty instance of your model
                print('row is', row)
               # print('product line is ', line)
                #warehouse_name = row['Deposito']

                #product_model.warehouse= Warehouses.objects.get(name=warehouse_name)
                product_model.name= row['Producto']
                product_model.barcode= row['CodigoOrigen']
                product_model.internalCode= row['Codigo']
                product_model.quantity= row['StockActual']
                product_model.category= row['Categoria']
                #product_model.location= row['Ubicacion']
                product_model.supplier= row['Proveedor']
                #print('warehouse is ', warehouse_name)
                print('i is',i)

                
                product_model.deltaQuantity= 0
                product_model.stockSecurity= row['StockSeguridad']
                product_model.inTransit = False

                print('product name is')
                print(product_model.name)
                
                objects.append(product_model)
            
            Product.objects.bulk_create(objects, ignore_conflicts=True)


        objects = []
        with open(new_products_file,  newline='', encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            i = 0
            for row in reader:
                #product_model = Product()
                warehouse_product_model = WarehousesProduct()
                i +=1  
                anaya_quantity = row['STOCK ANAYA 2710']
                crocker_quantity = row['STOCK CROKER']
                juanico_quantity = row['STOCK JUANICO']

                if anaya_quantity != '':
                    warehouse_product_model.name = 'Anaya 2710'
                    #product_model.name= row['Producto']
                    warehouse_product_model.product = Product.objects.get(row['Producto'])
                    warehouse_product_model.quantity = anaya_quantity
                    warehouse_product_model.location = row['Ubicacion Anaya']

                if crocker_quantity != '':
                    warehouse_product_model.name = 'Crocker'
                    warehouse_product_model.product = Product.objects.get(row['Producto'])
                    warehouse_product_model.quantity = crocker_quantity
                    warehouse_product_model.location = row['Ubicacion Crocker']

                if juanico_quantity != '':
                    warehouse_product_model.name = 'Juanico'
                    warehouse_product_model.product = Product.objects.get(row['Producto'])
                    warehouse_product_model.quantity = juanico_quantity
                    warehouse_product_model.location = row['Ubicacion Juanico']

            

                objects.append(warehouse_product_model)

            WarehousesProduct.objects.bulk_create(objects)
            
    # Populate the fields of the model based on the record line of your file
#    obj.field1 = line[0] # The first column
#    obj.field2 = line[1] # The second column
    # Add the model to the list of objects
 #   objects.append(obj)

# Save all objects simultaniously, instead of saving for each line
