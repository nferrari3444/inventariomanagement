from django.db import models
from django.contrib.auth.models import AbstractUser, AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import UserManager
from .managers import CustomUserManager

class CustomUser( AbstractBaseUser , PermissionsMixin ):
    
    class Meta:
        verbose_name = 'Usuarios'
        verbose_name_plural = 'Usuarios'

    username = models.CharField(max_length=40, verbose_name="Usuario")
    password = models.CharField(max_length=100)
    email = models.EmailField(max_length=40, blank=False, unique=True, 
                              default='', error_messages =
                                {'required': 'Please provide your email address.',
                  'unique': 'An account with this email exist'}, verbose_name="Correo")
    
    # 11-04-2024 Se le sacan los atributos de choices a departamento y role
    departamento = models.CharField(max_length=30,  default='Sales', verbose_name="Departamento")
    role = models.CharField(max_length=40,  blank=True, null=True, verbose_name= "Rol")
    
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    objects = CustomUserManager()

class Cotization(models.Model):
    
    cotization_id = models.AutoField(primary_key=True)
    date = models.DateField(verbose_name=u"Fecha", null=True, blank=True)
    customer = models.CharField(max_length=60, blank=True)
    numberOfProducts = models.IntegerField(null=True, blank=True)
    observations = models.CharField(max_length=500, blank= True)

# Tabla de Productos
class Product(models.Model):
      
    class Meta:
      verbose_name = 'Stock Productos vs Seguridad'
      verbose_name_plural = 'Stock Productos vs Seguridad'
    
    CURRENCIES= [('USD', 'Dolar'),
                  ('$', 'Pesos')]
    
    product_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    barcode = models.CharField(max_length= 100, null=True, blank=True, verbose_name=u"Codigo de Barras")
    internalCode = models.BigIntegerField(verbose_name=u"Codigo Interno")
    quantity = models.FloatField(default=0, null=True, blank=True)
    category = models.CharField(max_length=100, default='Insumos') 
    
    supplier = models.CharField(max_length=100, default='', null=True, blank=True )

    stockSecurity = models.IntegerField(default=0, null=True, blank=True)
    price = models.FloatField(default=0, null=True, blank=True, verbose_name="Precio de Lista")
    currency = models.CharField(max_length=10, choices=CURRENCIES, default='Dolar')
    hasOffer = models.ForeignKey(Cotization, on_delete=models.SET_DEFAULT, blank=True, null=True, default=None)
    quantityOffer = models.FloatField(null=True, blank= True)
    priceOffer = models.FloatField(null=True, blank= True)
    
    def __str__(self):
        return self.name
    
# Create your models here.
class WarehousesProduct(models.Model):
    
    class Meta:
        verbose_name = 'Productos en Deposito'
        verbose_name_plural = 'Productos en Deposito'

    name = models.CharField(max_length=100, verbose_name="Deposito")
    product = models.ForeignKey(Product, on_delete = models.CASCADE,  blank=True, null=True, verbose_name="Producto" )
    quantity = models.FloatField(default=0, null=True, blank=True, verbose_name="Cantidad en Deposito")
    location = models.CharField(max_length=100, null=True, blank=True, verbose_name="Ubicacion")
    deltaQuantity = models.FloatField()
    inTransit = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    
    def delete(self, *args, **kwargs):
        # create a new Activity
        activity = StockMovements()
        activity.actionType = self.name + " deleted!"

    
        # if using ForeignKey field
        activity.warehouseProduct = self
        # # if using IntegerField
        # activity.project = self.id

        super(WarehousesProduct, self).delete(*args, **kwargs)

    def __str__(self):
        return self.name

# Tabla para Ubicaciones
        
class Tasks(models.Model):
    STATUS = [('Pending','Pending'),
              ('Confirmed','Confirmed'),
              ('Cancelled', 'Cancelled')]


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

    receptor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='receptor',  blank=True, null=True)
    issuer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='issuer', blank=True, null=True)
    status = models.CharField(max_length=30, choices= STATUS, default='Pending')
    
    department = models.CharField(max_length=30, choices = DEPARTMENT, default='Sales')
    date = models.DateField(verbose_name=u"Fecha")
    deliveryDate = models.DateField(verbose_name=u"Fecha", default = '1970-01-01')

    motivoIngreso = models.CharField(max_length=30, choices = MOTIVOSINGRESO) # default='Transferencia Depósitos')
    motivoEgreso = models.CharField(max_length=30, choices = MOTIVOSEGRESO) #default='Transferencia Depósitos')

    warehouseProduct = models.ForeignKey(WarehousesProduct, on_delete= models.CASCADE, blank=True, null=True)
    actionType = models.CharField(max_length=20,  default='Inbound')
    observationsSolicitud = models.CharField(max_length=500,  blank= True)
    observationsConfirma = models.CharField(max_length=500,  blank= True)

class StockMovements(models.Model):
    
    class Meta:
      verbose_name = 'Detalle Movimiento Producto'
      verbose_name_plural = 'Detalle Movimientos Productos'

    MOVEMENT = [('Inbound','Inbound'),
                ('Outbound', 'Outbound')]
    
    # Se cambia Product como primary key por WarehousesProduct
    warehouseProduct = models.ForeignKey(WarehousesProduct, on_delete=models.CASCADE, null=True, verbose_name=u"Nombre de Producto")
    task = models.ForeignKey(Tasks, on_delete=models.CASCADE,  blank=True, null=True )
#date = models.DateField(verbose_name=u"Fecha")
  #  deliveryDate = models.DateField(verbose_name=u"Fecha", default = '1970-01-01')
    actionType = models.CharField(max_length=25,  default='Inbound')
    cantidad = models.FloatField(default=0)
    cantidadNeta = models.FloatField(default=0)
    cantidadEntregada = models.FloatField(default=0)
    image = models.ImageField(upload_to='images/', null=True, blank=True)
#    status = models.CharField(max_length=30, choices= STATUS, default='Pending')
    # warehouse = models.ForeignKey(Warehouses, on_delete= models.CASCADE, blank=True, null=True)



    
class DiffProducts(models.Model):
    
    class Meta:
      verbose_name = 'Faltante Producto Total'
      verbose_name_plural = 'Faltante Productos Total'

    warehouseProduct = models.ForeignKey(WarehousesProduct, on_delete= models.CASCADE, blank=True, null=True)
    totalPurchase = models.FloatField(verbose_name="Cantidad")
    totalQuantity = models.FloatField(verbose_name="Cantidad Neta")
    productDiff = models.IntegerField(verbose_name="Diferencia")
