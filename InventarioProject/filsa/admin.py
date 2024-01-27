from django.contrib import admin
from .models import Warehouses, Product, StockMovements, DiffProducts, CustomUser
# Register your models here.
admin.site.register(Warehouses)

admin.site.register(Product)
admin.site.register(StockMovements)
admin.site.register(DiffProducts)
admin.site.register(CustomUser)