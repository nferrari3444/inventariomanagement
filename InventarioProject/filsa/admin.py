from django.contrib import admin
from .models import Warehouses, Product, StockMovements, DiffProducts, CustomUser
from django.urls import reverse
from django.utils.html import format_html
from django.contrib.admin import SimpleListFilter
from django.db.models import F
# Register your models here.


class FaltanteFilter(SimpleListFilter):
    title = "Faltante"
    parameter_name = "Faltante"

    def lookups(self, request, model_admin):
        return [
            ("yes", "Yes"),
            ("no", "No"),
        ]

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(cantidad__gt = F('cantidadNeta')).filter(actionType='Confirma Ingreso')
        elif self.value() == "no":
            return queryset.exclude(cantidad__gt = F('cantidadNeta')).filter(actionType='Confirma Ingreso')
        else:
            return queryset.all()
        
class AdminStockMovements(admin.ModelAdmin):
    list_display = ["product","actionType","cantidad","cantidadNeta", "diferencia", "faltante"]
    list_select_related = ["product"]
    list_filter = ["product", FaltanteFilter]

    search_fields = ["product__name"]
    def diferencia(self, obj):
        if obj.actionType == "Confirma Ingreso":
            return obj.cantidad - obj.cantidadNeta  

    def faltante(self,obj):
        if obj.actionType == 'Confirma Ingreso':
            return obj.cantidad > obj.cantidadNeta
            
        
    diferencia.short_description = "Diferencia"
    faltante.boolean = True

class AdminProductDiff(admin.ModelAdmin):
 
    list_display = ["product", "warehouse", "totalPurchase", "totalQuantity", "productDiff"]
    list_select_related = ["product", "warehouse"]

    
    # def product_history(self, obj):
    #     link = reverse("admin:filsa_stockmovements", args=[obj.product.product_id])
    #     return format_html('<a href="{}">{}</a>', link, obj.product)

    # product_history.short_description = "Product History"

    search_fields = ["product", "product__name"]

admin.site.register(Warehouses)

admin.site.register(Product)
admin.site.register(StockMovements,AdminStockMovements)
admin.site.register(DiffProducts, AdminProductDiff)
admin.site.register(CustomUser)