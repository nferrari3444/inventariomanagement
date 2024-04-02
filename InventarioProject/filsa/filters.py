import django_filters
from .models import Product, WarehousesProduct
from django.forms import ModelChoiceField
from django import forms

class WarehouseChoiceFilter(django_filters.ChoiceFilter):
    @property
    def field(self):
        self.extra['choices'] = set([(a.name, a.name) for a in WarehousesProduct.objects.all()]) # self.parent.queryset])
        return super(WarehouseChoiceFilter, self).field

class CategoryChoiceFilter(django_filters.ChoiceFilter):
    @property
    def field(self):                                          #  Author.objects.prefetch_related('book_set').values('id', 'book')
        self.parent.queryset = [product for product in WarehousesProduct.objects.select_related('product')]          #Product.objects.all().values('category').distinct()
        self.extra['choices'] = set([(a.product.category,a.product.category) for a in self.parent.queryset])
       
        # self.form.fields['category'].widget.attrs.update({'class' : "ml-5 bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"}) 
        return super(CategoryChoiceFilter, self).field

class SupplierChoiceFilter(django_filters.ChoiceFilter):
    @property
    def field(self):
        self.parent.queryset = [product for product in WarehousesProduct.objects.select_related('product')] #    Product.objects.all().values('supplier').distinct()
        self.extra['choices'] = set([(a.product.supplier, a.product.supplier) for a in self.parent.queryset ])
        #self.extra.update({'widget' : forms.ChoiceField(attrs={'class': 'ml-5 bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500'})})
                          
        return super(SupplierChoiceFilter, self).field

# class StockWarehouseSet(django_filters.FilterSet):
#     name = WarehouseChoiceFilter(field_name='name')
#     class Meta:
#         model = WarehousesProduct
#         fields = ['name']


class StockFilterSet(django_filters.FilterSet):
    categories = Product.objects.all().values('category').distinct()
    suppliers = Product.objects.all().values('supplier').distinct()
    warehouses = WarehousesProduct.objects.all().values('name').distinct()
  
   
    #categoria = django_filters.ModelChoiceFilter(queryset= Product.objects.all().values('category').distinct())

    #supplier = django_filters.ModelChoiceFilter(field_name='supplier', queryset=Product.objects.values_list('supplier', flat=True).distinct())
    supplier = SupplierChoiceFilter(field_name='supplier')
    category = CategoryChoiceFilter(field_name='category')
    name = WarehouseChoiceFilter(field_name='name')

    # supplier = django_filters.ChoiceFilter(label='Proveedor',
    #  field_name='supplier' ,
    #    choices = Product.objects.values_list('supplier', flat=True).distinct(),
    #    widgets = forms.Select(attrs={'class': 'ml-5 bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500'}))
    # def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
    #         super(StockFilterSet, self).__init__(data=data, queryset=queryset, request=request, prefix=prefix)
    #         self.filters['supplier'].field.widget.attrs.update({'class': 'ml-5 bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500'})
   
    class Meta:
        model = WarehousesProduct
        #model = Product

       # fields = ['name',] # 'warehousesproduct__product__category','warehousesproduct__product__supplier']
        fields = ['name', 'supplier','category' ] 
        # widgets = {
        #     'supplier': forms.ChoiceField(widget= forms.ChoiceField(attrs={'class': 'ml-5 bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500'}))

        # }
    def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
        super().__init__(data, queryset, request=request, prefix=prefix)
        for f in self.filters.values():
            if isinstance(f, django_filters.ChoiceFilter):
                f.extra.update({'widget': forms.Select(attrs={'class' :'w-60 mr-2 sm:w-10 bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500'})})
    # def __init__(self, data, *args, **kwargs):
    #     data = data.copy()
    #     data.setdefault('format', 'name')
    #     data.setdefault('format', 'category')
    #     data.setdefault('format', 'supplier')
    #     data.setdefault('order', '-added')
    #     super().__init__(data, *args, **kwargs)