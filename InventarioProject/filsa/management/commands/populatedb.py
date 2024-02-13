from django.core.management.base import BaseCommand, CommandError
from filsa.models import CustomUser, StockMovements, DiffProducts, Product, Warehouses, Tasks


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

        warehouses_list = ['Anaya 2710' , 'Crocker 2652' , 'Juanico' ,'Taller', 'En Transito']

        
        warehouse_object = []
        for i in range(0,len(warehouses_list)):
            warehouses_model = Warehouses()
            warehouses_model.name = warehouses_list[i]
            warehouse_object.append(warehouses_model)

        Warehouses.objects.bulk_create(warehouse_object)


        #users_file = './usuariosFilsa.txt' 
        #products_file = './productosFilsa.txt' 
        users_file = 'C:/Users/nicol/Inventario/InventarioProject/filsa/management/commands/usuariosFilsa.txt'
        products_file = 'C:/Users/nicol/Inventario/InventarioProject/filsa/management/commands/productosFilsa.txt'
        #f = open(users_file, "r")
        #reader = f.read()
        #users_lines = list(reader)
        
        with open(users_file) as file:
        #     #print(file.readlines())
            users_lines = file.readlines()
        # # Archivo: Nombre,Correo,Contraseña, Deparamento,Rol
            users_obj = []
            for line in users_lines[1:]:
                
                user_model = CustomUser()
                print('user line is ', line)
                line = line.split(',')
                print(line)
        #         #nombre_usuario = line[0]
        #         #correo = line[1]
        #         #password = line[2]
        #         #departamento = line[3]
        #         #rol = line[4]
                print('username', line[0])
                user_model.username = line[0]
                print('email', line[2])
                user_model.email = line[2]
                user_model.password = line[1]
                user_model.departamento = line[3]
                user_model.role = line[4]
        #         #obj = CustomUser(username= nombre_usuario, password=password, email=correo, departamento=departamento,rol=rol)
        #         #obj.save()
                
                users_obj.append(user_model)


            CustomUser.objects.bulk_create(users_obj)




        #f = open(products_file, "r")
        #reader = f.read()
        #lines = list(reader)
        
        objects = []
        with open(products_file) as file:
            # print(file.readlines())
            product_lines = file.readlines()

            #print(f.read())

            # Create an empty list of objects of your model
            
          
            # Iterate each record of the csv file
            for line in product_lines[1:]:
                product_model = Product()
                # Create an empty instance of your model
                line = line.split(',')
                print('product line is ', line)
                warehouse_name = line[5]
                # nombre=line[0]
                # barcode = line[1]
                # internalCode = line[2]
                # category = line[3]
                # supplier = line[4]
                # warehouse_obj = Warehouses.objects.get(name=warehouse_name)
                # stockSecurity = line[6]
                # cantidad = line[7]
                # location = line[8]
                # deltaQuantity = line[9]
                # inTransit = line[10]

                # obj = Product(name=nombre, barcode=barcode,internalCode=internalCode,quantity=cantidad,
                #     category=category,location=location,supplier=supplier,warehouse=warehouse_obj,
                #     deltaQuantity=deltaQuantity,stockSecurity=stockSecurity,inTransit=inTransit)
                
                product_model.name= line[0] 
                product_model.barcode= line[1]
                product_model.internalCode= line[2]
                product_model.quantity= line[7]
                product_model.category= line[3]
                product_model.location= line[8]
                product_model.supplier= line[4]
                print('warehouse is ', warehouse_name)
                product_model.warehouse= Warehouses.objects.get(name=warehouse_name)
                product_model.deltaQuantity= line[9]
                product_model.stockSecurity= line[6]
                product_model.inTransit = False
                
                objects.append(product_model)
        
            Product.objects.bulk_create(objects)

    # Populate the fields of the model based on the record line of your file
#    obj.field1 = line[0] # The first column
#    obj.field2 = line[1] # The second column
    # Add the model to the list of objects
 #   objects.append(obj)

# Save all objects simultaniously, instead of saving for each line
