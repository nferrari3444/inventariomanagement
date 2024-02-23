from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.forms.utils import ValidationError
from django.forms import ModelChoiceField
from django.forms import modelformset_factory
from .models import (CustomUser, StockMovements, Product, DiffProducts , Warehouses, Tasks)


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

    issuer = forms.ModelChoiceField(queryset=CustomUser.objects.all()
                                      ,widget=forms.Select(attrs={
                                         'class': "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500",
                                         'style': 'max-width: auto;',
                                     }), empty_label='-------------', to_field_name='username')
    

#     BirdFormSet = modelformset_factory(
#            StockMovements, fields=("product", "cantidad"), extra=1
# )
    receptor = forms.ModelChoiceField(queryset=CustomUser.objects.all()
                                      ,widget=forms.Select(attrs={
                                         'class': "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500",
                                         'style': 'max-width: auto;',
                                     }), empty_label='-------------', to_field_name='username')

    warehouse = forms.ModelChoiceField(queryset=Warehouses.objects.all()
                                      ,widget=forms.Select(attrs={
                                         'class': "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500",
                                         'style': 'max-width: auto;',
                                     }), empty_label='-------------', to_field_name='name')

    
    
    class Meta:
        model = Tasks
        fields = ['warehouse','issuer','receptor','department','date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'})
        }
    
    
    def __init__(self, *args, **kwargs):
        
        extra_fields = kwargs.pop('extra',0)
        print('extra_fields line 64', extra_fields)

        super(TransferForm, self).__init__(*args, **kwargs)
        self.fields['extra_field_count'].initial = extra_fields
        self.fields['department'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500'})
        self.fields['date'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500'})

       # self.fields['extra_field_count'] = 

        for index in range(0, int(extra_fields) ):
            print('index in line 73 is {}'.format(index))
            self.fields['product_{index}'.format(index=index)] =   forms.CharField()
            
            self.fields['barcode_{index}'.format(index=index)] = forms.CharField()
            self.fields['internalCode_{index}'.format(index=index)] = forms.CharField()
            self.fields['cantidad_{index}'.format(index=index)] = forms.IntegerField()


class TransferReceptionForm(forms.ModelForm):
    extra_field_count = forms.CharField(widget=forms.HiddenInput())

    
    class Meta:
        model = Tasks
        # fields = ['product','department','issuer', 'motivoEgreso', 'cantidad', 'date',
        #           'receptor', 'cantidadEntregada', 'deliveryDate', 'warehouse']
        fields = ['department','issuer', 'date', 'receptor', 'warehouse'] #, 'task']
   
    def __init__(self, *args, **kwargs):
        
        extra_fields = kwargs.pop('extra',0)
        print('extra_fields', extra_fields)
        
        print('kwargs is :', kwargs)

        super(TransferReceptionForm, self).__init__(*args, **kwargs)


        self.fields['extra_field_count'].initial = extra_fields
        print('kwargs is :', kwargs)
    
        products = self.instance.stockmovements_set.all()
        print('products in Inbound Reception form are', products)
        for product in products:
            print('product in loop of line 127 form is ', product.product.name)
       
        print('self.instance is:', self.instance)
        self.fields['department'].widget.attrs.update({'class':'bg-gray-100 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500', 'disabled':True }) #= self.instance.department
        
        self.fields['receptor'].widget.attrs.update({'class':'bg-gray-100 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500', 'disabled':True })    #.widget.value_from_datadict = self.instance.receptor
        self.fields['warehouse'].widget.attrs.update({'class':'bg-white border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500'})      #.widget.value_from_datadict = self.instance.warehouse
        self.fields['issuer'].widget.attrs.update({'class':'bg-gray-100 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500', 'disabled':True }) #    .widget.value_from_datadict = self.instance.issuer
        self.fields['date'].widget.attrs.update({'class':'bg-gray-100 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500', 'disabled':True }) #    .widget.value_from_datadict = self.instance.issuer
        
        self.fields['department'].widget.value_from_datadict = lambda *args: self.instance.department
        self.fields['date'].widget.value_from_datadict = lambda *args: self.instance.date
        # self.fields['warehouse'].widget.value_from_datadict = lambda *args: self.instance.warehouse
        self.fields['receptor'].widget.value_from_datadict = lambda *args: self.instance.receptor
        self.fields['issuer'].widget.value_from_datadict = lambda *args: self.instance.issuer

        for i , product in enumerate(products):
            print('product in form loop is {} for i {}'.format(product.product.name,i))

            field_name = 'producto_{}'.format(i)
            quantity = 'cantidad_{}'.format(i)
            netQuantity = 'cantidadNeta_{}'.format(i)
            # print('product in form is {}'.format(product))

            print('product name in form is {}'.format(product.product.name))
            # print('product cantidad in form is {}'.format(product.cantidad))
            
            self.fields[field_name] = forms.CharField()
            self.fields[quantity] =  forms.CharField()
            self.fields[netQuantity] = forms.CharField()

            # self.fields[field_name].widget.attrs.update({'class':'bg-gray-200 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500', 'disabled':True }) #    .widget.value_from_datadict = self.instance.issuer
            self.fields[field_name].widget.value_from_datadict = lambda *args: product.product.name

            self.fields[quantity].widget.attrs.update({'type':'number' , 'class':'bg-gray-200 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500', 'disabled':True }) #    .widget.value_from_datadict = self.instance.issuer
            self.fields[quantity].widget.value_from_datadict = lambda *args: int(product.cantidad)

### Inbound Form
class InboundForm(forms.ModelForm):
    #original_field = forms.CharField()
    extra_field_count = forms.CharField(widget=forms.HiddenInput())

    issuer = forms.ModelChoiceField(queryset=CustomUser.objects.all()
                                      ,widget=forms.Select(attrs={
                                         'class': "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500",
                                         'style': 'max-width: auto;',
                                     }), empty_label='-------------', to_field_name='username')
    
    receptor = forms.ModelChoiceField(queryset=CustomUser.objects.all()
                                      ,widget=forms.Select(attrs={
                                         'class': "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500",
                                         'style': 'max-width: auto;',
                                     }), empty_label='-------------', to_field_name='username')

    warehouse = forms.ModelChoiceField(queryset=Warehouses.objects.all()
                                      ,widget=forms.Select(attrs={
                                                 
                                         'class': "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500",
                                         'style': 'max-width: auto;',
                                     }), empty_label='-------------', to_field_name='name')


    
    class Meta:
        model = Tasks
        fields = ['warehouse','motivoIngreso','issuer', 'receptor', 'department' , 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'})
        }
    
    
    def __init__(self, *args, **kwargs):
        
        extra_fields = kwargs.pop('extra',0)
        print('extra_fields line 64', extra_fields)

        super(InboundForm, self).__init__(*args, **kwargs)
        self.fields['extra_field_count'].initial = extra_fields
        self.fields['department'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500'})
        self.fields['motivoIngreso'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500'})
        self.fields['date'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500'})
       # self.fields['extra_field_count'] = 

        for index in range(0, int(extra_fields) ):
            print('index in line 73 is {}'.format(index))
            self.fields['product_{index}'.format(index=index)] =   forms.CharField()
            
            self.fields['barcode_{index}'.format(index=index)] = forms.CharField()
            self.fields['internalCode_{index}'.format(index=index)] = forms.CharField()
            self.fields['cantidad_{index}'.format(index=index)] = forms.IntegerField()

   

    # def __init__(self, *args, **kwargs):
    #     user = kwargs.pop('user','')
    #     print('args are', args)
    #     super(InboundForm, self).__init__(*args, **kwargs)
        
    #     self.fields['cantidad'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-1/2 p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500'})
    #     self.fields['cantidadNeta'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-1/2 p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500'})
    #     self.fields['motivoIngreso'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500'})
    #     self.fields['image'].required = False
       
    #     widgets = {
    #         'date': forms.widgets.DateInput(attrs={'type': 'date'}),
    #     }


    # def save(self, *args, **kwargs):
    #     product = args[0].get('product',None)
    #     print('product in save is', product)
    #     self.fields['product'] = product
    #     data = super(InboundForm, self).save(*args, **kwargs)
    #     return data
   
class InboundReceptionForm(forms.ModelForm):
    extra_field_count = forms.CharField(widget=forms.HiddenInput())

    
    class Meta:
        model = Tasks
        # fields = ['product','department','issuer', 'motivoEgreso', 'cantidad', 'date',
        #           'receptor', 'cantidadEntregada', 'deliveryDate', 'warehouse']
        fields = ['department','issuer', 'motivoIngreso', 'date', 'receptor', 'warehouse'] #, 'task']
   
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
            print('product in loop of line 127 form is ', product.product.name)
       
        print('self.instance is:', self.instance)
        self.fields['department'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500', 'disabled':True }) #= self.instance.department
        self.fields['motivoIngreso'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500', 'disabled':True })    #widget.value_from_datadict = self.instance.motivoIngreso
        self.fields['receptor'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500', 'disabled':True })    #.widget.value_from_datadict = self.instance.receptor
        self.fields['warehouse'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500', 'disabled':True })      #.widget.value_from_datadict = self.instance.warehouse
        self.fields['issuer'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500', 'disabled':True }) #    .widget.value_from_datadict = self.instance.issuer
        self.fields['date'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500', 'disabled':True }) #    .widget.value_from_datadict = self.instance.issuer
        
        self.fields['department'].widget.value_from_datadict = lambda *args: self.instance.department
        self.fields['motivoIngreso'].widget.value_from_datadict = lambda *args: self.instance.motivoIngreso
        self.fields['date'].widget.value_from_datadict = lambda *args: self.instance.date
        self.fields['warehouse'].widget.value_from_datadict = lambda *args: self.instance.warehouse
        self.fields['receptor'].widget.value_from_datadict = lambda *args: self.instance.receptor
        self.fields['issuer'].widget.value_from_datadict = lambda *args: self.instance.issuer

        for i , product in enumerate(products):
            print('product in form loop is {} for i {}'.format(product.product.name,i))

            field_name = 'producto_{}'.format(i)
            quantity = 'cantidad_{}'.format(i)
            netQuantity = 'cantidadNeta_{}'.format(i)
            # print('product in form is {}'.format(product))

            print('product name in form is {}'.format(product.product.name))
            # print('product cantidad in form is {}'.format(product.cantidad))
            
            self.fields[field_name] = forms.CharField()
            self.fields[quantity] =  forms.CharField()
            self.fields[netQuantity] = forms.CharField()

            self.fields[field_name].widget.attrs.update({'class':'bg-gray-150 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-1/2 p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500', 'disabled':True }) #    .widget.value_from_datadict = self.instance.issuer
            self.fields[field_name].widget.value_from_datadict = lambda *args: product.product.name

            self.fields[quantity].widget.attrs.update({'type':'number' , 'class':'bg-gray-150 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-1/2 p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500', 'disabled':True }) #    .widget.value_from_datadict = self.instance.issuer
            self.fields[quantity].widget.value_from_datadict = lambda *args: int(product.cantidad)

       

      #  for visible in self.visible_fields():
           # if visible.name == 'field_name':
      ##      print('self.fields name are', visible.name)
      #      print('self.fields value are', visible.value())
    

    # def save(self, *args, **kwargs):
    #     super(InboundReceptionForm, self).__init__(*args, **kwargs)
    #     products = self.instance.stockmovements_set.all()
    #     for i , product in enumerate(products):
            
    #         print('product in form loop is {} for i {}'.format(product.product.name,i))

    #         field_name = 'producto_{}'.format(i)
    #         quantity = 'cantidad_{}'.format(i)
    #         netQuantity = 'cantidadNeta_{}'.format(i)
    #         self.fields[field_name].widget.attrs.update({'class':'bg-gray-150 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-1/2 p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500', 'disabled':True }) #    .widget.value_from_datadict = self.instance.issuer
    #         self.fields[field_name].widget.value_from_datadict = lambda *args: product.product.name

    #         self.fields[quantity].widget.attrs.update({'type':'number' , 'class':'bg-gray-150 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-1/2 p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500', 'disabled':True }) #    .widget.value_from_datadict = self.instance.issuer
    #         self.fields[quantity].widget.value_from_datadict = lambda *args: int(product.cantidad)
   
    #     product = args[0].get('product',None)
    #     print('product in save is', product)
       # data =  super(InboundReceptionForm, self).save(*args, **kwargs)
      #  self.fields['product'] = product
      #  data = super(InboundForm, self).save(*args, **kwargs)
    #    return data
            
    def save(self, *args, **kwargs):
      
        meal = super(InboundReceptionForm, self).save(*args, **kwargs)

        print('meal is ', meal)

        return meal

### OutboundOrder Form
            
class OutboundOrderForm(forms.ModelForm):
    
    extra_field_count = forms.CharField(widget=forms.HiddenInput())
    # .values_list('username',flat=True)
    issuer = ModelChoiceField(queryset=CustomUser.objects.all()
                                       ,widget=forms.Select(attrs={
                                          'class': "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500",
                                          'style': 'max-width: auto;',
                                      }), empty_label='-------------', to_field_name=  'username')
    # # .values_list('name',flat=True)
    # product= ModelChoiceField(queryset=Product.objects.all()
    #                                   ,widget=forms.Select(attrs={
    #                                       'class': "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500",
    #                                       'style': 'max-width: auto;',
    #                                       'name': 'productname'
    #                                   }), empty_label='-------------', to_field_name='name')
  
    warehouse = forms.ModelChoiceField(queryset=Warehouses.objects.all()
                                      ,widget=forms.Select(attrs={
                                         'class': "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500",
                                         'style': 'max-width: auto;',
                                     }), empty_label='-------------', to_field_name='name')
    
    
    receptor = ModelChoiceField(queryset=CustomUser.objects.all()
                                       ,widget=forms.Select(attrs={
                                          'class': "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500",
                                          'style': 'max-width: auto;',
                                      }), empty_label='-------------', to_field_name=  'username')
    
    
    class Meta:
        model = Tasks
        # fields = ['product','department','issuer', 'motivoEgreso', 'cantidad', 'date']
        #fields = ['department','issuer', 'motivoEgreso', 'warehouse','date', 'receptor' ]
        fields = ['warehouse','motivoEgreso','issuer', 'receptor', 'department' , 'date']
   
    def __init__(self, *args, **kwargs):
        
        extra_fields = kwargs.pop('extra',0)
        print('extra_fields', extra_fields)

        super(OutboundOrderForm, self).__init__(*args, **kwargs)
        self.fields['extra_field_count'].initial = extra_fields
        self.fields['department'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500'})
        self.fields['motivoEgreso'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500'})
       # self.fields['extra_field_count'] = 

        for index in range(0, int(extra_fields) ):
            self.fields['producto_{index}'.format(index=index)] =   forms.CharField()
            
            self.fields['barcode_{index}'.format(index=index)] = forms.CharField()
            self.fields['internalCode_{index}'.format(index=index)] = forms.CharField()
            self.fields['cantidad_{index}'.format(index=index)] = forms.IntegerField()

 
        #CustomPK._meta.pk.name
       # self.fields['cantidad'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-1/2 p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500'})
      #  self.fields['department'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-1/2 p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500'})

   
    
### OutboundDelivery Form
class OutboundDeliveryForm(forms.ModelForm):
    extra_field_count = forms.CharField(widget=forms.HiddenInput())
    # receptor = ModelChoiceField(queryset=CustomUser.objects.all()
    #                                    ,widget=forms.Select(attrs={
    #                                       'class': "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500",
    #                                       'style': 'max-width: auto;',
    #                                   }), empty_label='-------------', to_field_name=  'username')
    
    # warehouse = forms.ModelChoiceField(queryset=Warehouses.objects.all()
    #                                   ,widget=forms.Select(attrs={
    #                                      'class': "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500",
    #                                      'style': 'max-width: auto;',
    #                                  }), empty_label='-------------', to_field_name='name')
    
    
    
    widgets = {
            'deliveryDate': forms.widgets.DateInput(attrs={'type': 'date'}),
         #   'cantidad': forms.Input(attrs={'class':"bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500"})
    }
    
    class Meta:
        model = Tasks
        # fields = ['product','department','issuer', 'motivoEgreso', 'cantidad', 'date',
        #           'receptor', 'cantidadEntregada', 'deliveryDate', 'warehouse']
        fields = ['department','issuer', 'motivoEgreso', 'date', 'receptor', 'warehouse']


    #def __init__(self, *args, **kwargs):
        
    def __init__(self, *args, **kwargs):
        
        extra_fields = kwargs.pop('extra',0)
        print('extra_fields', extra_fields)
        
        print('kwargs is :', kwargs)

        super(OutboundDeliveryForm, self).__init__(*args, **kwargs)
        self.fields['extra_field_count'].initial = extra_fields
        print('kwargs is :', kwargs)
        print('args are', *args)

        for visible in self.visible_fields():
           # if visible.name == 'field_name':
            print('self.fields name before update is', visible.name)
            print('self.fields value before update is ', visible.value())

        if self.instance:
            products = self.instance.stockmovements_set.all()
            print('products in form OutboundDelivery are', products)
            #numberOfProducts = 2
            for product in products:
                print('product in products of self.instance.stockmovements_set.all() is', product.product.name)
            #print('self.instance is:', self.instance.)
            self.fields['department'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500', 'disabled':True }) #= self.instance.department
            self.fields['motivoEgreso'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500', 'disabled':True })    #widget.value_from_datadict = self.instance.motivoIngreso
            self.fields['receptor'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500', 'disabled':True })    #.widget.value_from_datadict = self.instance.receptor
            self.fields['warehouse'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500', 'disabled':True })      #.widget.value_from_datadict = self.instance.warehouse
            self.fields['issuer'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500', 'disabled':True }) #    .widget.value_from_datadict = self.instance.issuer
            self.fields['date'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500', 'disabled':True }) #    .widget.value_from_datadict = self.instance.issuer
            
            self.fields['department'].widget.value_from_datadict = lambda *args: self.instance.department
            self.fields['motivoEgreso'].widget.value_from_datadict = lambda *args: self.instance.motivoEgreso
            self.fields['date'].widget.value_from_datadict = lambda *args: self.instance.date
            self.fields['warehouse'].widget.value_from_datadict = lambda *args: self.instance.warehouse
            self.fields['receptor'].widget.value_from_datadict = lambda *args: self.instance.receptor
            self.fields['issuer'].widget.value_from_datadict = lambda *args: self.instance.issuer

            for i , product in enumerate(products):
            #     print('product in form is {} with i {}'.format(product.product.name,i))
            #     print('product lambda', lambda *args: product.product.name[i])

                field_name = 'producto_{}'.format(i)
                quantity = 'cantidad_{}'.format(i)
                netQuantity = 'cantidadNeta_{}'.format(i)
                # print('product in form is {}'.format(product))

                # print('product name in form is {}'.format(product.product.name))
                # print('product cantidad in form is {}'.format(product.cantidad))
                
                self.fields[field_name] = forms.CharField()
                self.fields[quantity] =  forms.CharField()
                self.fields[netQuantity] = forms.CharField()

                #self.initial[field_name] = product.product.name 
                self.fields[field_name].widget.attrs.update({'class':'bg-gray-300 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500', 'disabled':True }) #    .widget.value_from_datadict = self.instance.issuer
                #print('-----------------------------------------------------------')
                #print('self.fields[field_name] before value is ', self.fields[field_name])

                #self.initial[field_name] =  product.product.name
                self.fields[field_name].widget.value_from_datadict = lambda *args: product.product.name
                #print('-----------------------------------------------------------')
                #print('self.fields[field_name] after value is ', self.fields[field_name])
                
            #  self.initial[field_name] = product.product.name

                #self.initial[quantity] = int(product.cantidad)
                self.fields[quantity].widget.attrs.update({'type':'number' ,  'class':'bg-gray-150 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-1/2 p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500', 'disabled':True }) #    .widget.value_from_datadict = self.instance.issuer
            #  self.initial[quantity] = int(product.cantidad)
                self.fields[quantity].widget.value_from_datadict =  lambda *args: int(product.cantidad)
            #  self.initial[quantity] = product.cantidad

    #     print('self.fields are', self.fields)
        for visible in self.visible_fields():
           if visible.name == 'field_name':
               print('self.fields name are', visible.name)
               print('self.fields value are', visible.value())

    def save(self, *args, **kwargs):
      
        meal = super(OutboundDeliveryForm, self).save(*args, **kwargs)
        return meal