from typing import Any
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.db import models
from .models import WarehousesProduct, Product, StockMovements, DiffProducts, CustomUser
from django.urls import reverse
from django.utils.html import format_html
from django.contrib.admin import SimpleListFilter
from django.db.models import F,ExpressionWrapper, FloatField, Sum
from import_export.admin import ExportActionMixin
from django.db.models import Q
from django.contrib.admin.views.decorators import staff_member_required
# Register your models here.
import csv

class Offer(SimpleListFilter):

    title = "Tiene Oferta"
    parameter_name = "Oferta"

    def lookups(self, request, model_admin):
        return [
            ("yes", "Yes"),
            ("no", "No"),
        ]

    
    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(hasOffer__isnull=False)
        elif self.value() == "no":
            return queryset.filter(hasOffer__isnull=True)
    
        
class StatusProducto(SimpleListFilter):
    title = "Status Producto"
    parameter_name = "Status Producto"

    def lookups(self, request, model_admin):
        return [
            ("critico", "Critico"),
            ("alerta", "Alerta"),
            ("normal", "Normal"),
        ]

    def queryset(self, request, queryset):
        if self.value() == "critico":
            return queryset.filter(quantity__lte = F('stockSecurity') * 1.2)
        if self.value() == "alerta":
            return queryset.filter(quantity__gte= F('stockSecurity') * 1.2).filter(quantity__lte = F('stockSecurity') * 1.5 ).filter(quantity__gt  = 0)
        if self.value() == 'normal':
            return queryset.filter(quantity__gte = F('stockSecurity') * 1.5 ).filter(quantity__gt  = 0)
            
        
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
            return queryset.filter(actionType='Confirma Ingreso')
        
class AdminStockMovements(ExportActionMixin, admin.ModelAdmin):
    list_display = ["date", "producto", "internalCode", "faltante", "Ingreso", "warehouse", "cantidad","cantidadNeta", "diferencia"]
    list_select_related = ["warehouseProduct"]
    list_filter = [FaltanteFilter]
    search_fields = ["warehouseProduct__product__name", "warehouseProduct__product__internalCode"]

    #"actionType",

    @admin.display(description='Codigo')
    def internalCode(self, obj):
        return obj.warehouseProduct.product.internalCode
    
    @admin.display(ordering='task__motivoIngreso', description='Tipo Ingreso')
    def Ingreso(self, obj):
        return obj.task.motivoIngreso
    
    @admin.display(ordering='task__deliveryDate', description='Fecha')
    def date(self, obj):
        return obj.task.deliveryDate
    
    
    @admin.display(description='Deposito')
    def warehouse(self, obj):
        return obj.warehouseProduct.name
    
    @admin.display(description='Producto')
    def producto(self, obj):
        return obj.warehouseProduct.product.name
    

    # def motivoIngreso(self, obj):
    #     return obj.task.name
    # get_name.admin_order_field  = 'author'  #Allows column order sorting
    # get_name.short_description = 'Author Name'  #Renames column head

    
    def diferencia(self, obj):
        if obj.actionType == "Confirma Ingreso":
            return obj.cantidad - obj.cantidadNeta  

    def faltante(self,obj):
        if obj.actionType == 'Confirma Ingreso':
            return obj.cantidad == obj.cantidadNeta
            
        
    diferencia.short_description = "Diferencia"
    faltante.boolean = True

class StockSecurity(ExportActionMixin, admin.ModelAdmin):

    products = Product.objects.filter(quantity__lt = F('stockSecurity') * 1.1)

    list_display = ["status_order", "name", "internalCode", "status_product",  "quantity", "stockSecurity", "oferta"]

    list_filter = [StatusProducto, Offer]
    search_fields = ["name", "internalCode"]

    # ordering= ["quantity"]
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        qs = super(StockSecurity, self).get_queryset(request)
        qs = qs.annotate(stock_rate= ExpressionWrapper(F('quantity') * 1.0 / F('stockSecurity'), output_field=FloatField())).order_by('stock_rate')
    
        return qs
    
    def status_order(self, obj):
        return obj.stock_rate
    
    
    def oferta(self, obj):
        if obj.hasOffer:
            return obj.hasOffer.cotization.customer
        else:
            return ''
        
    status_order.admin_order_field =  'status_order'

    def status_product(self,obj):
        
        if obj.quantity <= obj.stockSecurity * 1.2:
            color = 'red'
            status = 'Critico'

            return format_html(
            '<b style="background:{};">{}</b>',
            color,status)
        
        if ((obj.quantity > obj.stockSecurity * 1.2) and (obj.quantity <= obj.stockSecurity * 1.5)):
            color = 'yellow'
            status = 'Alerta'

            return format_html(
            '<b style="background:{};">{}</b>',
            color,status)
        
        if obj.quantity > obj.stockSecurity * 1.5:
            color = 'green'
            status = 'Normal'

            return format_html(
            '<b style="background:{};">{}</b>',
            color,status)
        
        return status
    

class AdminProductDiff(ExportActionMixin, admin.ModelAdmin):
 
    list_display = ["product", "warehouse", "totalPurchase", "totalQuantity", "productDiff"]
    list_select_related = ["warehouseProduct"]

    #search_fields = ["product", "product__name"]

    @admin.display(description='Producto')
    def product(self, obj):
        return obj.warehouseProduct.product.name
    
    
    # def receipt_amount(self, request):
    #     current_receipt_purchase_amounts = StockMovements.objects.filter(WarehousesProduct = request.id).values_list('price', flat = True)
    #     total_amount = sum(current_receipt_purchase_amounts)
    #     return total_amount
    # receipt_amount.short_description = 'Receipt Amount'

    @admin.display(description='Deposito')
    def warehouse(self, obj):
        return obj.warehouseProduct.name
    
    # def product_history(self, obj):
    #     link = reverse("admin:filsa_stockmovements", args=[obj.product.product_id])
    #     return format_html('<a href="{}">{}</a>', link, obj.product)

    # product_history.short_description = "Product History"

    

admin.site.register(WarehousesProduct)

admin.site.register(Product,StockSecurity)
# admin.site.register(StockSecurity)
admin.site.register(StockMovements,AdminStockMovements)
admin.site.register(DiffProducts, AdminProductDiff)
admin.site.register(CustomUser)