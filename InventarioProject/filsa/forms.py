from django import forms
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm
from django.db import transaction
from django.forms.utils import ValidationError
from django.forms import ModelChoiceField
from django.forms import modelformset_factory
from .models import (CustomUser, StockMovements, Product, DiffProducts , WarehousesProduct, Tasks)


class SignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser

    def save(self, commit=True):
        user = super().save(commit=False)
        # user.is_teacher = True
        if commit:
            user.save()
        return user

class DateInput(forms.DateInput):
    input_type = 'date'

### Transfer Form
class TransferForm(forms.ModelForm):
    extra_field_count = forms.CharField(widget=forms.HiddenInput())

    # receptor = forms.ModelChoiceField(queryset=CustomUser.objects.all()
    #                                   ,widget=forms.Select(attrs={
    #                                      'class': "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500",
    #                                      'style': 'max-width: auto;',
    #                                  }), empty_label='-------------', to_field_name='username')

    warehouse = forms.ModelChoiceField(queryset=WarehousesProduct.objects.values_list('name', flat=True ).exclude(name='No Stock').exclude(name='En Transito').distinct()
                                      ,widget=forms.Select(attrs={
                                         'class': "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500",
                                        'id':'warehouse',
                                         "name":'warehouse',

                                         'style': 'max-width: auto;',
                                     }), empty_label='-------------', to_field_name='name')

    observationsSolicitud = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows':4, 'class': "block p-2.5 w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500" , 'placeholder': "Observaciones..."}))

    class Meta:
        model = Tasks
        fields = ['issuer','receptor','department','date','observationsSolicitud']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'})
        }
    
    
    def __init__(self, *args, **kwargs):
        
        extra_fields = kwargs.pop('extra',0)
        print('extra_fields line 64', extra_fields)
        user = kwargs.pop('user')
        print('args in tranfer from invalid', *args)
        super(TransferForm, self).__init__(*args, **kwargs)
        taskToEdit = kwargs.pop('instance', [])
        print('taskToEdit is', taskToEdit)
        form_data = args
        # invalidForm = kwargs.pop('invalidForm')

       
        if taskToEdit:
            self.fields['warehouse'].widget.value_from_datadict =  lambda *args: taskToEdit.warehouseProduct.name
            self.fields['warehouse'].initial =  taskToEdit.warehouseProduct.name
            self.fields['warehouse'].widget.attrs.update({'class':'bg-white-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500'})
            self.fields['receptor'].widget.attrs.update({'class':'bg-white-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500' })    #.widget.value_from_datadict = self.instance.receptor
            self.fields['receptor'].initial =  taskToEdit.receptor
            #self.fields['receptor'].widget.value_from_datadict = lambda *args: self.instance.receptor
            self.fields['date'].initial =  taskToEdit.date
            # self.fields['motivoEgreso'].initial =  taskToEdit.motivoEgreso
            self.fields['observationsSolicitud'].initial =  taskToEdit.observationsSolicitud

            self.fields['date'].widget = forms.DateInput(
                   format=('%Y-%m-%d'),
                    attrs={'class': 'form-control', 
                        'placeholder': 'Select a date',
                        'type': 'date'
              })
      
        self.fields['extra_field_count'].initial = extra_fields
        self.fields['department'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500'})
        self.fields['date'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500'})
        self.fields['issuer'].initial = user
        self.fields['issuer'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500', 'disabled': True})
        self.fields['receptor'].widget.attrs.update({'class':'bg-white-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500'})


        for index in range(1, int(extra_fields) + 1 ):
            print('index in line 73 is {}'.format(index))
            self.fields['product_{index}'.format(index=index)] =   forms.CharField()
            
            #self.fields['barcode_{index}'.format(index=index)] = forms.CharField()
            self.fields['internalCode_{index}'.format(index=index)] = forms.CharField()
            self.fields['cantidad_{index}'.format(index=index)] = forms.IntegerField()
        

       # self.fields['extra_field_count'] = 
        # if invalidForm == True:
        #     for index in range(1, int(extra_fields) + 1 ):
        #         #self.fields['product_{index}'.format(index=index)] =   args[0]['product_{index}'.format(index=index)]
            
        #         # #self.fields['barcode_{index}'.format(index=index)] = forms.CharField()
        #         #self.fields['internalCode_{index}'.format(index=index)] = args[0]['internalCode_{index}'.format(index=index)]
        #         #self.fields['cantidad_{index}'.format(index=index)] = args[0]['cantidad_{index}'.format(index=index)]
        #         print('product is', args[0]['product_{index}'.format(index=index)])
        #         print('internalCode is', args[0]['internalCode_{index}'.format(index=index)])
        #         print('cantidad is', args[0]['cantidad_{index}'.format(index=index)])
        

            
        
    def clean(self):
        extra_fields = self.cleaned_data['extra_field_count']
        warehouse = self.cleaned_data['warehouse']
        self.data = self.data.copy()
        
        for index in range(1, int(extra_fields) + 1):
            
            product = self.cleaned_data['product_{index}'.format(index=index)]
            internalCode = self.cleaned_data['internalCode_{index}'.format(index=index)]
            productStockInWarehouse = WarehousesProduct.objects.filter(product__internalCode= internalCode, name=warehouse)
            #if  WarehousesProduct.objects.filter(product__name=product, name=warehouse).exists():  #Product.objects.filter(name = product, warehouse=warehouse).exists():

            product_db = Product.objects.get(internalCode = internalCode)
            product_stock = product_db.quantity
            stockSecurity = product_db.stockSecurity
            print('product in method is {}'.format(product))
            print('product in stock is {}'.format(product_stock))
            print('product stockSecurity is {}'.format(stockSecurity))
            print('product_db in clean method is {}'.format(product_db))

            quantity_warehouse = productStockInWarehouse[0].quantity
            quantity = self.cleaned_data['cantidad_{index}'.format(index=index)]
            if quantity_warehouse - quantity < 0:
                raise ValidationError("La cantidad ingresada por {} del producto {} , es mayor a la cantidad en stock de {} en el deposito {}".format(quantity, product , quantity_warehouse, warehouse))

            #else:
            #    raise ValidationError('El Producto {} no se encuentra en el deposito {}'.format(product,warehouse))

class TransferReceptionForm(forms.ModelForm):
    extra_field_count = forms.CharField(widget=forms.HiddenInput())
    observationsConfirma = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows":"5", "class" : "block p-2.5 w-full mt-2 text-sm text-gray-900 bg-white-50 rounded-lg border border-gray-300 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500" ,"placeholder":"Your description here"}))
    
    
    warehouse = forms.ModelChoiceField(queryset=WarehousesProduct.objects.values_list('name', flat=True ).exclude(name='No Stock').distinct()
                                      ,widget=forms.Select(attrs={
                                         'class': "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500",
                                        'id':'warehouse',
                                         "name":'warehouse',

                                         'style': 'max-width: auto;',
                                     }), empty_label='-------------', to_field_name='name')

    warehouseSalida = forms.CharField()
    observationsSolicitud = forms.CharField(required=False)

    class Meta:
        model = Tasks
        # fields = ['product','department','issuer', 'motivoEgreso', 'cantidad', 'date',
        #           'receptor', 'cantidadEntregada', 'deliveryDate', 'warehouse']
        fields = ['department','issuer', 'date', 'receptor', 'observationsConfirma'] #, 'task']
   
    def __init__(self, *args, **kwargs):
        
        extra_fields = kwargs.pop('extra',0)
        print('extra_fields', extra_fields)
        
        print('kwargs is :', kwargs)

        super(TransferReceptionForm, self).__init__(*args, **kwargs)


        self.fields['extra_field_count'].initial = extra_fields
        print('kwargs is :', kwargs)
        
        products = self.instance.stockmovements_set.all().filter(actionType='Transferencia')
        print('products in Inbound Reception form are', products)
        for product in products:
            print('product in loop of line 127 form is ', product.warehouseProduct.product)   #product.product.name)
       
        print('self.instance is:', self.instance)
        self.fields['department'].widget.attrs.update({'class':'bg-gray-100 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500', 'disabled':True }) #= self.instance.department
        
        self.fields['receptor'].widget.attrs.update({'class':'bg-gray-100 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500', 'disabled':True })    #.widget.value_from_datadict = self.instance.receptor
        self.fields['warehouse'].widget.attrs.update({'class':'bg-white border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500'})      #.widget.value_from_datadict = self.instance.warehouse
        self.fields['issuer'].widget.attrs.update({'class':'bg-gray-100 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500', 'disabled':True }) #    .widget.value_from_datadict = self.instance.issuer
        self.fields['date'].widget.attrs.update({'class':'bg-gray-100 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500', 'disabled':True }) #    .widget.value_from_datadict = self.instance.issuer
        
        self.fields['warehouseSalida'].widget.attrs.update({'class':'bg-gray-100 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500', 'disabled':True })
        self.fields['observationsSolicitud'].widget.attrs.update({'class': "block p-2.5 w-full text-sm text-gray-900 bg-gray-100 rounded-lg border border-gray-300 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500"})
        
        self.fields['department'].widget.value_from_datadict = lambda *args: self.instance.department
        self.fields['date'].widget.value_from_datadict = lambda *args: self.instance.date
        #self.fields['warehouseSalida'].widget.value_from_datadict = lambda *args: self.instance.warehouse
        #self.fields['warehouseSalida'].initial = self.instance.warehouseProduct.name
        self.fields['warehouseSalida'].widget.value_from_datadict = lambda *args: self.instance.warehouseProduct.name
        self.fields['warehouseSalida'].initial =  self.instance.warehouseProduct.name
        self.fields['observationsSolicitud'].widget.value_from_datadict = lambda *args: self.instance.observationsSolicitud

        self.fields['observationsSolicitud'].initial = lambda *args: self.instance.observationsSolicitud
        self.fields['receptor'].widget.value_from_datadict = lambda *args: self.instance.receptor
        # self.fields['issuer'].widget.value_from_datadict = lambda *args: self.instance.issuer
        #self.fields['issuer'].initial = user
        for i , product in enumerate(products):
            print('product in form loop is {} for i {}'.format(product.warehouseProduct.product.name,i))

            field_name = 'producto_{}'.format(i)
            quantity = 'cantidad_{}'.format(i)
            netQuantity = 'cantidadNeta_{}'.format(i)
            # print('product in form is {}'.format(product))

            #print('product name in form is {}'.format(product.product.name))
            # print('product cantidad in form is {}'.format(product.cantidad))
            
            self.fields[field_name] = forms.CharField()
            self.fields[quantity] =  forms.CharField()
            self.fields[netQuantity] = forms.CharField()

            # self.fields[field_name].widget.attrs.update({'class':'bg-gray-200 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500', 'disabled':True }) #    .widget.value_from_datadict = self.instance.issuer
            self.fields[field_name].widget.value_from_datadict = lambda *args: product.warehouseProduct.product.name

            self.fields[quantity].widget.attrs.update({'type':'number' , 'class':'bg-gray-200 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500', 'disabled':True }) #    .widget.value_from_datadict = self.instance.issuer
            self.fields[quantity].widget.value_from_datadict = lambda *args: int(product.cantidad)

### Inbound Form
class InboundForm(forms.ModelForm):
    #original_field = forms.CharField()
    extra_field_count = forms.CharField(widget=forms.HiddenInput())
    # receptor = forms.ModelChoiceField(queryset=CustomUser.objects.all()
    #                                   ,widget=forms.Select(attrs={
    #                                      'class': "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500",
    #                                      'style': 'max-width: auto;',
    #                                  }), empty_label='-------------', to_field_name='username')

    warehouse = forms.ModelChoiceField(queryset=WarehousesProduct.objects.values_list('name', flat=True).exclude(name='No Stock').exclude(name='En Transito').distinct()
                                      ,widget=forms.Select(attrs={
                                                 
                                         'class': "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500",
                                         'style': 'max-width: auto;',
                                     }), empty_label='-------------', to_field_name='name')

    observationsSolicitud = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows':4, 'class': "block p-2.5 w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500" , 'placeholder': "Observaciones..."}))

   
    class Meta:
        model = Tasks
        fields = ['motivoIngreso','issuer', 'receptor', 'department' , 'date', 'observationsSolicitud']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'})
        }
    
    
    def __init__(self, *args, **kwargs):
        
        extra_fields = kwargs.pop('extra',0)
        print('extra_fields line 64', extra_fields)
        user = kwargs.pop('user')
        super(InboundForm, self).__init__(*args, **kwargs)
        taskToEdit = kwargs.pop('instance', [])
        
        if taskToEdit:
            self.fields['warehouse'].widget.value_from_datadict =  lambda *args: taskToEdit.warehouseProduct.name
            self.fields['warehouse'].initial =  taskToEdit.warehouseProduct.name
            self.fields['warehouse'].widget.attrs.update({'class':'bg-white-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500'})
            self.fields['receptor'].widget.attrs.update({'class':'bg-white-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500' })    #.widget.value_from_datadict = self.instance.receptor
            self.fields['receptor'].initial =  taskToEdit.receptor
        #     self.fields['receptor'].widget.value_from_datadict = lambda *args: self.instance.receptor
            self.fields['date'].initial =  taskToEdit.date
            self.fields['motivoIngreso'].initial =  taskToEdit.motivoIngreso
            self.fields['observationsSolicitud'].initial =  taskToEdit.observationsSolicitud

            self.fields['date'].widget = forms.DateInput(
                   format=('%Y-%m-%d'),
                    attrs={'class': 'form-control', 
                        'placeholder': 'Select a date',
                        'type': 'date'
              })
                    
        
        self.fields['extra_field_count'].initial = extra_fields
        self.fields['department'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500'})
        self.fields['motivoIngreso'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500'})
        self.fields['date'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500'})
       # self.fields['extra_field_count'] = 
        self.fields['issuer'].initial = user
        self.fields['issuer'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500', 'disabled': True})
        self.fields['receptor'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500'})

        for index in range(1, int(extra_fields) + 1):
            print('index in line 73 is {}'.format(index))
            self.fields['producto_{index}'.format(index=index)] =   forms.CharField()
            
            #self.fields['barcode_{index}'.format(index=index)] = forms.CharField()
            self.fields['internalCode_{index}'.format(index=index)] = forms.CharField()
            self.fields['cantidad_{index}'.format(index=index)] = forms.IntegerField()
   
class InboundReceptionForm(forms.ModelForm):
    extra_field_count = forms.CharField(widget=forms.HiddenInput())
    observationsConfirma = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows":"5", "class" : "block p-2.5 w-full text-sm text-gray-900 bg-white-50 rounded-lg border border-gray-300 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500" ,"placeholder":"Your description here"}))

    warehouse = forms.ModelChoiceField(queryset=WarehousesProduct.objects.values_list('name', flat=True).distinct()
                                      ,widget=forms.Select(attrs={
                                                 
                                         'class': "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500",
                                         'style': 'max-width: auto;',
                                     }), empty_label='-------------', to_field_name='name')

    observationsSolicitud = forms.CharField(required=False)

    class Meta:
        model = Tasks
        # fields = ['product','department','issuer', 'motivoEgreso', 'cantidad', 'date',
        #           'receptor', 'cantidadEntregada', 'deliveryDate', 'warehouse']
#       fields = ['department','issuer', 'motivoIngreso', 'date', 'receptor', 'warehouse','observations'] #, 'task']
        fields = ['department','issuer', 'motivoIngreso', 'date', 'receptor','observationsConfirma'] #, 'task']
    
    def __init__(self, *args, **kwargs):
        
        extra_fields = kwargs.pop('extra',0)
        print('extra_fields', extra_fields)
        
        print('kwargs is :', kwargs)

        super(InboundReceptionForm, self).__init__(*args, **kwargs)


        self.fields['extra_field_count'].initial = extra_fields
        print('kwargs is :', kwargs)
    
        products = self.instance.stockmovements_set.all()
        print('products in Inbound Reception form are', products)
        for product in products:
            print('product in loop of line 127 form is ', product.warehouseProduct.product.name)
       
        print('self.instance is:', self.instance)
        self.fields['department'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500', 'disabled':True }) #= self.instance.department
        self.fields['motivoIngreso'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500', 'disabled':True })    #widget.value_from_datadict = self.instance.motivoIngreso
        self.fields['receptor'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500', 'disabled':True })    #.widget.value_from_datadict = self.instance.receptor
        self.fields['warehouse'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500', 'disabled':True })      #.widget.value_from_datadict = self.instance.warehouse
        self.fields['issuer'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500', 'disabled':True }) #    .widget.value_from_datadict = self.instance.issuer
        self.fields['date'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500', 'disabled':True }) #    .widget.value_from_datadict = self.instance.issuer
        self.fields['observationsSolicitud'].widget.attrs.update({'class': "block p-2.5 w-full text-sm text-gray-900 bg-white-100 rounded-lg border border-gray-300 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500"})


        self.fields['department'].widget.value_from_datadict = lambda *args: self.instance.department
        self.fields['motivoIngreso'].widget.value_from_datadict = lambda *args: self.instance.motivoIngreso
        self.fields['date'].widget.value_from_datadict = lambda *args: self.instance.date
        self.fields['warehouse'].widget.value_from_datadict = lambda *args: self.instance.warehouseProduct.name
        self.fields['warehouse'].initial =  self.instance.warehouseProduct.name
        self.fields['receptor'].widget.value_from_datadict = lambda *args: self.instance.receptor
        self.fields['issuer'].widget.value_from_datadict = lambda *args: self.instance.issuer
        self.fields['observationsSolicitud'].initial = lambda *args: self.instance.observationsSolicitud

        for i , product in enumerate(products):
            print('product in form loop is {} for i {}'.format(product.warehouseProduct.product.name,i))

            field_name = 'producto_{}'.format(i)
            quantity = 'cantidad_{}'.format(i)
            netQuantity = 'cantidadNeta_{}'.format(i)
            # print('product in form is {}'.format(product))

            print('product name in form is {}'.format(product.warehouseProduct.product.name))
            # print('product cantidad in form is {}'.format(product.cantidad))
            
            self.fields[field_name] = forms.CharField()
            self.fields[quantity] =  forms.CharField()
            self.fields[netQuantity] = forms.CharField()

            self.fields[field_name].widget.attrs.update({'class':'bg-gray-150 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-1/2 p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500', 'disabled':True }) #    .widget.value_from_datadict = self.instance.issuer
            self.fields[field_name].widget.value_from_datadict = lambda *args: product.warehouseProduct.product.name

            self.fields[quantity].widget.attrs.update({'type':'number' , 'class':'bg-gray-150 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-1/2 p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500', 'disabled':True }) #    .widget.value_from_datadict = self.instance.issuer
            self.fields[quantity].widget.value_from_datadict = lambda *args: int(product.cantidad)

            
    def save(self, *args, **kwargs):
      
        meal = super(InboundReceptionForm, self).save(*args, **kwargs)

        print('meal is ', meal)

        return meal

### OutboundOrder Form
            
class OutboundOrderForm(forms.ModelForm):
    
    extra_field_count = forms.CharField(widget=forms.HiddenInput())
     
    warehouse = forms.ModelChoiceField(queryset=WarehousesProduct.objects.values_list('name', flat=True).exclude(name='No Stock').exclude(name='En Transito').distinct()
                                      ,widget=forms.Select(attrs={
                                         'class': "bg-white-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500",
                                         'id':'warehouse',
                                         "name":'warehouse',
                                         'style': 'max-width: auto;',
                                     }), empty_label='-------------', to_field_name='name')
    
    
    # receptor = ModelChoiceField(queryset=CustomUser.objects.all()
    #                                    ,widget=forms.Select(attrs={
    #                                       'class': "bg-white-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500",
    #                                       'style': 'max-width: auto;',
    #                                   }), empty_label='-------------', to_field_name=  'username')
    
    observationsSolicitud = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows':4, 'class': "block p-2.5 w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500" , 'placeholder': "Observaciones..."}))

    class Meta:
        model = Tasks
        # fields = ['product','department','issuer', 'motivoEgreso', 'cantidad', 'date']
        #fields = ['department','issuer', 'motivoEgreso', 'warehouse','date', 'receptor' ]
       # fields = ['warehouse','motivoEgreso', 'issuer', 'receptor', 'department' , 'date']
        fields = ['motivoEgreso', 'issuer', 'receptor', 'department' , 'date']
    
    def __init__(self, *args, **kwargs):
        
        extra_fields = kwargs.pop('extra',0)
        user = kwargs.pop('user')
        taskToEdit = kwargs.pop('instance', [])
        #args.pop('extra_field_count')
        print('*args ', *args)
        print('args ', args)
        print('extra_fields', extra_fields)
        print('taskToEdit is', taskToEdit)

        super(OutboundOrderForm, self).__init__(*args, **kwargs)

        print('self.is_bound is', self.is_bound)

        self.fields['extra_field_count'].initial = extra_fields
        self.fields['issuer'].initial = user
        print('args is' , args)
        print('kwargs is', kwargs)
        print('user is', user)

        if taskToEdit:
            self.fields['warehouse'].widget.value_from_datadict =  lambda *args: taskToEdit.warehouseProduct.name
            self.fields['warehouse'].initial =  taskToEdit.warehouseProduct.name
            self.fields['warehouse'].widget.attrs.update({'class':'bg-white-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500'})
            self.fields['receptor'].widget.attrs.update({'class':'bg-white-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500' })    #.widget.value_from_datadict = self.instance.receptor
            self.fields['receptor'].initial =  taskToEdit.receptor
        #     self.fields['receptor'].widget.value_from_datadict = lambda *args: self.instance.receptor
            self.fields['date'].initial =  taskToEdit.date
            self.fields['motivoEgreso'].initial =  taskToEdit.motivoEgreso
            self.fields['observationsSolicitud'].initial =  taskToEdit.observationsSolicitud

            self.fields['date'].widget = forms.DateInput(
                   format=('%Y-%m-%d'),
                    attrs={'class': 'form-control', 
                        'placeholder': 'Select a date',
                        'type': 'date'
              })
                    
        
        
        self.fields['department'].widget.attrs.update({'class':'bg-white-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500'})
        self.fields['motivoEgreso'].widget.attrs.update({'class':'bg-white-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500'})

        self.fields['date'].widget.attrs.update({'class':'bg-white-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500'})


        self.fields['issuer'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500', 'disabled': True})
        
        self.fields['receptor'].widget.attrs.update({'class':'bg-white-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500'})
        self.fields['warehouse'].widget.attrs.update({'class':'bg-white-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500'})
    
        
        #self.fields['issuer'].widget.value_from_datadict = lambda *args: self.instance.user
    # self.fields['extra_field_count'] = 

        for index in range(1, int(extra_fields) +1):
            self.fields['producto_{index}'.format(index=index)] =   forms.CharField()             
            # self.fields['barcode_{index}'.format(index=index)] = forms.CharField()
            self.fields['internalCode_{index}'.format(index=index)] = forms.CharField()
            self.fields['cantidad_{index}'.format(index=index)] = forms.IntegerField()

   
    def clean(self):
        extra_fields = self.cleaned_data['extra_field_count']
        warehouse = self.cleaned_data['warehouse']
        print('self.cleaned_data', self.cleaned_data)
        for index in range(1, int(extra_fields) + 1):
            print('index in clean form is', index)
            product = self.cleaned_data['producto_{index}'.format(index=index)]
            internalCode = self.cleaned_data['internalCode_{index}'.format(index=index)]
            print('product warehouse is ')
            product_db = Product.objects.filter(internalCode = internalCode)

            productStockInWarehouse = WarehousesProduct.objects.filter(product__internalCode= internalCode, name=warehouse)
            #product = self.cleaned_data['producto_{index}'.format(index=index)]
            #if  WarehousesProduct.objects.filter(product__name= product, name=warehouse).exists():            #Product.objects.filter(name = product, warehouse=warehouse).exists():

            product_db = Product.objects.get(internalCode = internalCode)
            productWarehouse_db = WarehousesProduct.objects.get(product = product_db, name = warehouse)
            product_stock = productWarehouse_db.quantity
            stockSecurity = product_db.stockSecurity
            print('product in method is {}'.format(product))
            print('product in stock is {}'.format(product_stock))
            print('product stockSecurity is {}'.format(stockSecurity))
            print('product_db in clean method is {}'.format(product_db))

            quantity = self.cleaned_data['cantidad_{index}'.format(index=index)]
            quantity_warehouse = productStockInWarehouse[0].quantity
            if quantity_warehouse - quantity < 0:
                raise ValidationError("La cantidad ingresada por {} del producto {} , es mayor a la cantidad en stock de {} en el deposito {}".format(quantity, product , quantity_warehouse, warehouse))

            #if  quantity > product_stock:
            #    raise ValidationError("La cantidad ingresada por {} del producto {} supera la cantidad en stock en el deposito {}".format(quantity, product , warehouse))
        #else:
        #    raise ValidationError('El producto {} no se encuentra en el deposito {}'.format(product,warehouse))

    def save(self, *args, **kwargs):
      
        meal = super(OutboundOrderForm, self).save(*args, **kwargs)
        return meal
    
### OutboundDelivery Form
class OutboundDeliveryForm(forms.ModelForm):
    extra_field_count = forms.CharField(widget=forms.HiddenInput())
  
    observationsConfirma = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows":"5", "class" : "block p-2.5 w-full text-sm text-gray-900 bg-white-50 rounded-lg border border-gray-300 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500" ,"placeholder":"Your description here"}))
    
    warehouse = forms.CharField()  
    
    observationsSolicitud = forms.CharField(required=False)

    widgets = {
            'deliveryDate': forms.widgets.DateInput(attrs={'type': 'date'}),
         #   'cantidad': forms.Input(attrs={'class':"bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500"})
    }
    
    class Meta:
        model = Tasks
        # fields = ['product','department','issuer', 'motivoEgreso', 'cantidad', 'date',
        #           'receptor', 'cantidadEntregada', 'deliveryDate', 'warehouse']
#        fields = ['department','issuer', 'motivoEgreso', 'date', 'receptor', 'warehouse', 'observations']
        fields = ['department','issuer', 'motivoEgreso', 'date', 'receptor', 'observationsConfirma']



    #def __init__(self, *args, **kwargs):
        
    def __init__(self, *args, **kwargs):
        
        extra_fields = kwargs.pop('extra',0)
        print('extra_fields', extra_fields)
        
        print('kwargs is :', kwargs)

        super(OutboundDeliveryForm, self).__init__(*args, **kwargs)
        self.fields['extra_field_count'].initial = extra_fields
       
        print('kwargs is :', kwargs)
        print('args are', *args)

        if self.instance:
            products = self.instance.stockmovements_set.all().filter(actionType='Nuevo Egreso')
            print('products in form OutboundDelivery are', products)
            #numberOfProducts = 2
            for product in products:
                print('product in products of self.instance.stockmovements_set.all() is', product.warehouseProduct.product.name)
            #print('self.instance is:', self.instance.)
          
            self.fields['department'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500', 'disabled':True }) #= self.instance.department
            self.fields['motivoEgreso'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500', 'disabled':True })    #widget.value_from_datadict = self.instance.motivoIngreso
            self.fields['receptor'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500', 'disabled':True })    #.widget.value_from_datadict = self.instance.receptor
                 #.widget.value_from_datadict = self.instance.warehouse
            self.fields['issuer'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500', 'disabled':True }) #    .widget.value_from_datadict = self.instance.issuer
            self.fields['date'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500', 'disabled':True }) #    .widget.value_from_datadict = self.instance.issuer
            self.fields['observationsSolicitud'].widget.attrs.update({'class': "block p-2.5 w-full text-sm text-gray-900 bg-gray-100 rounded-lg border border-gray-300 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500"})


            self.fields['department'].widget.value_from_datadict = lambda *args: self.instance.department
            self.fields['motivoEgreso'].widget.value_from_datadict = lambda *args: self.instance.motivoEgreso
            self.fields['date'].widget.value_from_datadict = lambda *args: self.instance.date
            self.fields['warehouse'].widget.value_from_datadict =  lambda *args: self.instance.warehouseProduct.name
            self.fields['warehouse'].initial =  self.instance.warehouseProduct.name
            self.fields['warehouse'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500', 'disabled':True })
            self.fields['receptor'].widget.value_from_datadict = lambda *args: self.instance.receptor
            self.fields['issuer'].widget.value_from_datadict = lambda *args: self.instance.issuer
            self.fields['observationsSolicitud'].initial = lambda *args: self.instance.observationsSolicitud

            for i , product in enumerate(products):
          
                field_name = 'producto_{}'.format(i)
                quantity = 'cantidad_{}'.format(i)
                netQuantity = 'cantidadNeta_{}'.format(i)
               
                
                self.fields[field_name] = forms.CharField()
                self.fields[quantity] =  forms.CharField()
                self.fields[netQuantity] = forms.CharField()

                #self.initial[field_name] = product.product.name 
                self.fields[field_name].widget.attrs.update({'class':'bg-gray-300 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500', 'disabled':True }) #    .widget.value_from_datadict = self.instance.issuer
                #print('-----------------------------------------------------------')
                #print('self.fields[field_name] before value is ', self.fields[field_name])

                #self.initial[field_name] =  product.product.name
                self.fields[field_name].widget.value_from_datadict = lambda *args: product.warehouseProduct.product.name
             
                #self.initial[quantity] = int(product.cantidad)
                self.fields[quantity].widget.attrs.update({'type':'number' ,  'class':'bg-gray-150 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-1/2 p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500', 'disabled':True }) #    .widget.value_from_datadict = self.instance.issuer
            #  self.initial[quantity] = int(product.cantidad)
                self.fields[quantity].widget.value_from_datadict =  lambda *args: int(product.cantidad)

    def save(self, *args, **kwargs):
      
        meal = super(OutboundDeliveryForm, self).save(*args, **kwargs)
        return meal
    
class CustomSetPasswordForm(SetPasswordForm):
    
    new_password1 = forms.CharField()
    new_password2 = forms.CharField()
    
    def __init__(self, *args, **kwargs):
        self.fields['new_password_1'].widget.attrs.update({'class':'bg-gray-150 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-1/2 p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500'})
        self.fields['new_password_2'].widget.attrs.update({'class':'bg-gray-150 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-1/2 p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500'})

class CrudProductsForm(forms.Form):
    
    archivo = forms.FileField(widget=forms.FileInput(attrs={'class': "mb-4 block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 dark:text-gray-400 focus:outline-none dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400" ,'id':"file_input" ,'type':"file" }))

class CotizationForm(forms.Form):

   # file = forms.FileInput()
    # <!-- <label class="block mb-2 text-sm font-medium text-gray-900 dark:text-white" for="file_input">Upload file</label>
    # <input class="block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 dark:text-gray-400 focus:outline-none dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400" id="file_input" type="file"> -->
   
    archivo = forms.FileField(widget=forms.FileInput(attrs={'class': "mb-4 block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 dark:text-gray-400 focus:outline-none dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400" ,'id':"file_input" ,'type':"file" }))
     
    cliente = forms.CharField(widget=forms.TextInput(attrs={"class" : "mt-4 block p-2.5 w-1/2 text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500" ,"placeholder":"Cliente"}))
   
    observaciones = forms.CharField(widget=forms.Textarea(attrs={"rows":"5", "class" : "mt-4 block p-2.5 w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500" ,"placeholder":"Your description here"}))
  


#     def __init__(self, *args, **kwargs):
#         super(CotizationForm, self).__init__(*args, **kwargs)
# #        self.fields['file'].widget.attrs.update({'class': 'myfieldclass'})
#         self.fields['file'].widget.attrs.update({'class': "block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 dark:text-gray-400 focus:outline-none dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400" ,'id':"file_input" ,'type':"file" })
   
    
    
        
       