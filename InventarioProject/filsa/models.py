from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    ROLES = [('Operator', 'Operator'),
             ('Logistic','Logistic'),
             ('Supervisor','Supervisor')]
    
    DEPARTMENT = [('Ventas','Ventas'),
                ('Planta Armado', 'Planta Armado'),
                ('Administración', 'Administraicón'),
                ('Servicio Técnico', 'Servicio Técnico'),
                ('Logística','Logística')
                ]
    
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    email = models.EmailField(max_length=50, blank=False, unique=True, 
                              default='', error_messages =
                                {'required': 'Please provide your email address.',
                  'unique': 'An account with this email exist'},)
    
    departamento = models.CharField(max_length=30, choices = DEPARTMENT, default='Sales')
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    role = models.CharField(max_length=40, choices=ROLES, blank=True, null=True)
    # isAdmin = models.BooleanField()

# Create your models here.
class Warehouses(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


# Tabla para Ubicaciones

# Tabla de Productos
class Product(models.Model):
    CATEGORIES = [('Tubos', 'Tubos'),
                  ('Tornillos', 'Tornillos'),
                  ('Accesorios','Accesorios'),
                  ('Maquinas','Maquinas')
                  ]
    
    product_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    barcode = models.BigIntegerField(verbose_name=u"Codigo de Barras")
    internalCode = models.BigIntegerField(verbose_name=u"Codigo Interno")
    quantity = models.FloatField()
    category = models.CharField(max_length=20, choices=CATEGORIES, default='Tubos')
    location = models.CharField(max_length=20)
    supplier = models.CharField(max_length=20)
    warehouse = models.ForeignKey(Warehouses, on_delete=models.CASCADE, related_name='warehouse_name')
    deltaQuantity = models.FloatField()
    stockSecurity = models.IntegerField()
    inTransit = models.BooleanField()



    def __str__(self):
        return self.name
   

class StockMovements(models.Model):
    MOVEMENT = [('Inbound','Inbound'),
                ('Outbound', 'Outbound')]
    
    STATUS = [('Pending','Pending'),
              ('Confirmed','Confirmed')]
    
    DEPARTMENT = [('Ventas','Ventas'),
                ('Planta Armado', 'Planta Armado'),
                ('Administración', 'Administraicón'),
                ('Servicio Técnico', 'Servicio Técnico'),
                ('Logística','Logística')
                ]
    
    MOTIVOSINGRESO = [('Transferencia Depósitos', 'Transferencia Depósitos'),
                ('Importación', 'Importación'),
                 ('Compra en Plaza', 'Compra en Plaza'),
                 ('Armado Nuevo Producto', 'Armado Nuevo Producto' )]
    
    MOTIVOSEGRESO = [('Servicio Técnico', 'Servicio Técnico'),
                     ('Planta de Armado', 'Planta de Armado'),
                      ('Ventas', 'Ventas'),
                       ('Mantenimiento', 'Mantenimiento') ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE,  verbose_name=u"Nombre de Producto")
    date = models.DateField(verbose_name=u"Fecha")
    deliveryDate = models.DateField(verbose_name=u"Fecha", default = '1970-01-01')
    actionType = models.CharField(max_length=20,  default='Inbound')
    receptor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='receptor',  blank=True, null=True)
    department = models.CharField(max_length=30, choices = DEPARTMENT, default='Sales')
    issuer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='issuer', blank=True, null=True)
    cantidad = models.FloatField(default=0)
    cantidadNeta = models.FloatField(default=0)
    cantidadEntregada = models.FloatField(default=0)
    motivoIngreso = models.CharField(max_length=30, choices = MOTIVOSINGRESO, default='Transferencia Depósitos')
    motivoEgreso = models.CharField(max_length=30, choices = MOTIVOSEGRESO, default='Transferencia Depósitos')
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    status = models.CharField(max_length=30, choices= STATUS, default='Pending')
    warehouse = models.ForeignKey(Warehouses, on_delete= models.CASCADE, blank=True, null=True)

class DiffProducts(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouses, on_delete= models.CASCADE, blank=True, null=True)
    totalPurchase = models.FloatField()
    totalQuantity = models.FloatField()
    productDiff = models.IntegerField()