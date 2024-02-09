from ..models import CustomUser, StockMovements, DiffProducts, Product, Warehouses, Tasks

warehouses_list = ['Anaya 2710' , 'Crocker 2652' , 'Juanico' ,'Taller', 'En Tránsito']

for i in range(0,len(warehouses_list)):
    warehouses = Warehouses(name=warehouses_list[i])



users_file = './usuariosFilsa.txt' 
f = open(users_file, "r")
reader = f.read()
users_lines = list(reader)

# Archivo: Nombre,Correo,Contraseña, Deparamento,Rol
users_obj = []
for line in users_lines:
    nombre_usuario = line[0]
    correo = line[1]
    password = line[2]
    departamento = line[3]
    rol = line[4]

    obj = CustomUser(username= nombre_usuario, password=password, email=correo, departamento=departamento,rol=rol)

    users_obj.append(obj)


CustomUser.objects.bulk_create(users_obj)



products_file = './productosFilsa.txt' 
f = open(products_file, "r")
reader = f.read()
lines = list(reader)

print(f.read())

# Create an empty list of objects of your model
objects = []

# Iterate each record of the csv file
for line in lines:
    # Create an empty instance of your model
    
    warehouse_name = line[5]
    nombre=line[0]
    barcode = line[1]
    internalCode = line[2]
    category = line[3]
    supplier = line[4]
    warehouse_obj = Warehouses.objects.get(name=warehouse_name)
    stockSecurity = line[6]
    cantidad = line[7]
    location = line[8]
    deltaQuantity = line[9]
    inTransit = line[10]

    obj = Product(name=nombre, barcode=barcode,internalCode=internalCode,quantity=cantidad,
                  category=category,location=location,supplier=supplier,warehouse=warehouse_obj,
                  deltaQuantity=deltaQuantity,stockSecurity=stockSecurity,inTransit=inTransit)
    objects.append(obj)
    
    # Populate the fields of the model based on the record line of your file
#    obj.field1 = line[0] # The first column
#    obj.field2 = line[1] # The second column
    # Add the model to the list of objects
 #   objects.append(obj)

# Save all objects simultaniously, instead of saving for each line
Product.objects.bulk_create(objects)