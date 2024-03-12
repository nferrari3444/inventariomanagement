from django.db import models
from django.contrib.auth.models import AbstractUser, AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import UserManager
from .managers import CustomUserManager

class CustomUser( AbstractBaseUser , PermissionsMixin ):
    
    ROLES = [('Operator', 'Operator'),
             ('Logistic','Logistic'),
             ('Supervisor','Supervisor')]
    
    DEPARTMENT = [('Ventas','Ventas'),
                
                ('Dirección', 'Dirección'),
                ('Administración', 'Administración'),
                ('Taller', 'Taller'),
                ('Logística','Logística')
                ]
  
    
    username = models.CharField(max_length=40)
    password = models.CharField(max_length=100)
    email = models.EmailField(max_length=40, blank=False, unique=True, 
                              default='', error_messages =
                                {'required': 'Please provide your email address.',
                  'unique': 'An account with this email exist'},)
    
    departamento = models.CharField(max_length=30, choices = DEPARTMENT, default='Sales')
    role = models.CharField(max_length=40, choices=ROLES, blank=True, null=True)
    
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    # @property
    # def is_active(self):
    #     return self.active
    

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    
  
    
    objects = CustomUserManager()
    
    # isAdmin = models.BooleanField()

# Create your models here.
class Warehouses(models.Model):
    name = models.CharField(max_length=40)

    def __str__(self):
        return self.name


# Tabla para Ubicaciones

# Tabla de Productos
class Product(models.Model):
    CATEGORIES = [('Tubos', 'Tubos'),
                  ('Tornillos', 'Tornillos'),
                  ('Accesorios','Accesorios'),
                  ('Maquinas','Maquinas'),
                  ('Insumos','Insumos')
                  ]
    
    # class Meta:
    #     unique_together = (('product_id', 'warehouse'),)

    product_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=40)
    barcode = models.CharField(max_length= 100, verbose_name=u"Codigo de Barras")
    internalCode = models.BigIntegerField(verbose_name=u"Codigo Interno")
    quantity = models.FloatField()
    category = models.CharField(max_length=20, choices=CATEGORIES, default='Insumos')
    location = models.CharField(max_length=20, default='')
    supplier = models.CharField(max_length=20, default='')
    warehouse = models.ForeignKey(Warehouses, on_delete=models.CASCADE, related_name='warehouse_name')
    deltaQuantity = models.FloatField()
    stockSecurity = models.IntegerField()
    inTransit = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name

  
   
class Tasks(models.Model):
    STATUS = [('Pending','Pending'),
              ('Confirmed','Confirmed')]


    DEPARTMENT = [('Ventas','Ventas'),
                ('Dirección', 'Dirección'),
                ('Administración', 'Administración'),
                 ('Encargado Servicio Técnico', 'Encargado Servicio Técnico'),
                ('Servicio Técnico', 'Servicio Técnico'),
                ('Logística','Logística')
                ]

    MOTIVOSINGRESO = [('Devolución Mercadería', 'Devolución Mercadería'),
                ('Importación', 'Importación'),
                 ('Compra en Plaza', 'Compra en Plaza'),
                 ('Armado Nuevo Producto', 'Armado Nuevo Producto' )]

    MOTIVOSEGRESO = [('Servicio Técnico', 'Servicio Técnico'),
                     ('Planta de Armado', 'Planta de Armado'),
                      ('Ventas', 'Ventas'),
                       ('Mantenimiento', 'Mantenimiento') ]
    
    task_id = models.AutoField(primary_key=True)
#    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
  #  department = models.CharField(max_length=30, choices = DEPARTMENT, default='Sales')
    receptor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='receptor',  blank=True, null=True)
    issuer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='issuer', blank=True, null=True)
    status = models.CharField(max_length=30, choices= STATUS, default='Pending')
    
    department = models.CharField(max_length=30, choices = DEPARTMENT, default='Sales')
    date = models.DateField(verbose_name=u"Fecha")
    deliveryDate = models.DateField(verbose_name=u"Fecha", default = '1970-01-01')

    motivoIngreso = models.CharField(max_length=30, choices = MOTIVOSINGRESO) # default='Transferencia Depósitos')
    motivoEgreso = models.CharField(max_length=30, choices = MOTIVOSEGRESO) #default='Transferencia Depósitos')

    warehouse = models.ForeignKey(Warehouses, on_delete= models.CASCADE, blank=True, null=True)
    actionType = models.CharField(max_length=20,  default='Inbound')
    observations = models.CharField(max_length=500, null=True, blank= True)
   # date = models.DateField(verbose_name=u"Fecha")
#deliveryDate = models.DateField(verbose_name=u"Fecha", default = '1970-01-01')
#actionType = models.CharField(max_length=20,  default='Inbound')


class StockMovements(models.Model):
    
    class Meta:
      verbose_name = 'Detalle Movimiento Producto'
      verbose_name_plural = 'Detalle Movimientos Productos'

    MOVEMENT = [('Inbound','Inbound'),
                ('Outbound', 'Outbound')]
    
       
    product = models.ForeignKey(Product, on_delete=models.CASCADE,  verbose_name=u"Nombre de Producto")
    task = models.ForeignKey(Tasks, on_delete=models.CASCADE,  blank=True, null=True )
#date = models.DateField(verbose_name=u"Fecha")
  #  deliveryDate = models.DateField(verbose_name=u"Fecha", default = '1970-01-01')
    actionType = models.CharField(max_length=25,  default='Inbound')
    
  #  receptor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='receptor',  blank=True, null=True)
    # department = models.CharField(max_length=30, choices = DEPARTMENT, default='Sales')
  #  issuer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='issuer', blank=True, null=True)
    cantidad = models.FloatField(default=0)
    cantidadNeta = models.FloatField(default=0)
    cantidadEntregada = models.FloatField(default=0)
    # motivoIngreso = models.CharField(max_length=30, choices = MOTIVOSINGRESO, default='Transferencia Depósitos')
    # motivoEgreso = models.CharField(max_length=30, choices = MOTIVOSEGRESO, default='Transferencia Depósitos')
    image = models.ImageField(upload_to='images/', null=True, blank=True)
#    status = models.CharField(max_length=30, choices= STATUS, default='Pending')
    # warehouse = models.ForeignKey(Warehouses, on_delete= models.CASCADE, blank=True, null=True)



    
class DiffProducts(models.Model):
    
    class Meta:
      verbose_name = 'Faltante Producto Total'
      verbose_name_plural = 'Faltante Productos Total'
     
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouses, on_delete= models.CASCADE, blank=True, null=True)
    totalPurchase = models.FloatField()
    totalQuantity = models.FloatField()
    productDiff = models.IntegerField()

class Cotization(models.Model):
    
    name = models.CharField(max_length=60)

    quantityBooked = models.IntegerField()

    product = models.ForeignKey(Product, on_delete=models.CASCADE)