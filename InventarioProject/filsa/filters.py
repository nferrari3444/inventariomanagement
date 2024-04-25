import django_filters
from .models import Product, WarehousesProduct
from django.forms import ModelChoiceField
from django import forms

class WarehouseChoiceFilter(django_filters.ChoiceFilter):
    @property
    def field(self):
        self.extra['choices'] = set([(a.name, a.name) for a in WarehousesProduct.objects.all().order_by('name')]) # self.parent.queryset])
        return super(WarehouseChoiceFilter, self).field

class CategoryChoiceFilter(django_filters.ChoiceFilter):
    @property
    def field(self):                                          #  Author.objects.prefetch_related('book_set').values('id', 'book')
        self.parent.queryset = [product for product in WarehousesProduct.objects.select_related('product').order_by('product__category')]          #Product.objects.all().values('category').distinct()
        self.extra['choices'] = set([(a.product.category,a.product.category) for a in self.parent.queryset])
       
        # self.form.fields['category'].widget.attrs.update({'class' : "ml-5 bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"}) 
        return super(CategoryChoiceFilter, self).field

class LocationChoiceFilter(django_filters.ChoiceFilter):
    @property
    def field(self):                                          #  Author.objects.prefetch_related('book_set').values('id', 'book')
        
        self.extra['choices'] = set([(a.location, a.location) for a in WarehousesProduct.objects.all().order_by('location')])
       
        # self.form.fields['category'].widget.attrs.update({'class' : "ml-5 bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"}) 
        return super(LocationChoiceFilter, self).field
    
class SupplierChoiceFilter(django_filters.ChoiceFilter):
    @property
    def field(self):
        self.parent.queryset = [product for product in WarehousesProduct.objects.select_related('product').order_by('product__supplier')] #    Product.objects.all().values('supplier').distinct()
        self.extra['choices'] = set([(a.product.supplier, a.product.supplier) for a in self.parent.queryset ])
        #self.extra.update({'widget' : forms.ChoiceField(attrs={'class': 'ml-5 bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500'})})
                          
        return super(SupplierChoiceFilter, self).field


class StockFilterSet(django_filters.FilterSet):
    
    supplier = SupplierChoiceFilter(field_name='supplier')
    category = CategoryChoiceFilter(field_name='category')
    name = WarehouseChoiceFilter(field_name='name')
    location = LocationChoiceFilter(field_name='location')

    
    class Meta:
        model = WarehousesProduct
        #model = Product

       # fields = ['name',] # 'warehousesproduct__product__category','warehousesproduct__product__supplier']
        fields = ['name', 'supplier','category' ,'location'] 
        # widgets = {
        #     'supplier': forms.ChoiceField(widget= forms.ChoiceField(attrs={'class': 'ml-5 bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500'}))

        # }
    def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
        super().__init__(data, queryset, request=request, prefix=prefix)
        for f in self.filters.values():
            if isinstance(f, django_filters.ChoiceFilter):
                f.extra.update({'widget': forms.Select(attrs={'class' :'w-40 mr-2 sm:w-10 bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500'})})
                