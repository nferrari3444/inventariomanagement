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

# class DateInput(forms.DateInput):
#     input_type = 'date'


### Inbound Form
class InboundForm(forms.ModelForm):
    #original_field = forms.CharField()
    extra_field_count = forms.CharField(widget=forms.HiddenInput())

    
#     BirdFormSet = modelformset_factory(
#            StockMovements, fields=("product", "cantidad"), extra=1
# )
    # receptor = forms.ModelChoiceField(queryset=CustomUser.objects.all()
    #                                   ,widget=forms.Select(attrs={
    #                                      'class': "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500",
    #                                      'style': 'max-width: auto;',
    #                                  }), empty_label='-------------', to_field_name='username')

    # warehouse = forms.ModelChoiceField(queryset=Warehouses.objects.all()
    #                                   ,widget=forms.Select(attrs={
    #                                      'class': "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500",
    #                                      'style': 'max-width: auto;',
    #                                  }), empty_label='-------------', to_field_name='name')

    def __init__(self, *args, **kwargs):
        
        extra_fields = kwargs.pop('extra',0)
        print('extra_fields', extra_fields)

        super(InboundForm, self).__init__(*args, **kwargs)
        self.fields['extra_field_count'].initial = extra_fields
        
       # self.fields['extra_field_count'] = 

        for index in range(0, int(extra_fields) + 1):
            self.fields['product_{index}'.format(index=index)] =   forms.CharField()
            
            self.fields['barcode_{index}'.format(index=index)] = forms.CharField()
            self.fields['internalCode_{index}'.format(index=index)] = forms.CharField()
            self.fields['cantidad_{index}'.format(index=index)] = forms.IntegerField()

    class Meta:
        model = Tasks
        fields = ['warehouse','motivoIngreso','issuer', 'receptor', 'department']

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

    receptor = ModelChoiceField(queryset=CustomUser.objects.all()
                                       ,widget=forms.Select(attrs={
                                          'class': "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500",
                                          'style': 'max-width: auto;',
                                      }), empty_label='-------------', to_field_name=  'username')
    
    warehouse = forms.ModelChoiceField(queryset=Warehouses.objects.all()
                                      ,widget=forms.Select(attrs={
                                         'class': "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500",
                                         'style': 'max-width: auto;',
                                     }), empty_label='-------------', to_field_name='name')
    
    #task =  forms.ModelChoiceField(queryset=None)
    
    widgets = {
            'deliveryDate': forms.widgets.DateInput(attrs={'type': 'date'}),
         #   'cantidad': forms.Input(attrs={'class':"bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500"})
    }
    
    class Meta:
        model = Tasks
        # fields = ['product','department','issuer', 'motivoEgreso', 'cantidad', 'date',
        #           'receptor', 'cantidadEntregada', 'deliveryDate', 'warehouse']
        fields = ['department','issuer', 'motivoIngreso', 'date', 'receptor', 'warehouse'] #, 'task']

    def __init__(self, *args, **kwargs):
        
        
        super(InboundReceptionForm, self).__init__(*args, **kwargs)
       # numberOfProducts = self.instance.stockmovements_set.all()
        print('kwargs is :', kwargs['initial']['task_id'])
        task_id =  kwargs['initial']['task_id']
     #   self.fields['task'].queryset = Tasks.objects.filter(task_id=task_id)  #self.instance
        print('self.instance is:', self.instance)
        self.fields['department'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-1/2 p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500', 'disabled':True }) #= self.instance.department
        self.fields['motivoIngreso'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-1/2 p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500', 'disabled':True })    #widget.value_from_datadict = self.instance.motivoIngreso
        self.fields['receptor'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-1/2 p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500', 'disabled':True })    #.widget.value_from_datadict = self.instance.receptor
        self.fields['warehouse'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-1/2 p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500', 'disabled':True })      #.widget.value_from_datadict = self.instance.warehouse
        self.fields['issuer'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-1/2 p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500', 'disabled':True }) #    .widget.value_from_datadict = self.instance.issuer
        #self.fields['cantidad'] = self.instance.stockmovements_set.values_list('cantidad',flat=True)
        #self.fields['products'] = [self.instance.stockmovements_set.all()[i].product.name for i in range(0,len(numberOfProducts))]
        #self.fields['products'] = self.instance.stockmovements_set.all()
        #print("self.fields['products']", self.fields['products'])
      
        # #self.data.update({ 'product': self.instance.product })
        # self.fields['product'].widget.value_from_datadict = lambda *args: self.instance.product
        # self.fields['department'].widget.value_from_datadict = lambda *args: self.instance.department
        # self.fields['motivoEgreso'].widget.value_from_datadict = lambda *args: self.instance.motivoEgreso
        # self.fields['cantidad'].widget.value_from_datadict = lambda *args: self.instance.cantidad
        # self.fields['deliveryDate'].widget.value_from_datadict = lambda *args: self.instance.deliveryDate

   

    def save(self, *args, **kwargs):
      
        meal = super(InboundReceptionForm, self).save(*args, **kwargs)
        return meal

### OutboundOrder Form
            
class OutboundOrderForm(forms.ModelForm):

    # .values_list('username',flat=True)
    issuer = ModelChoiceField(queryset=CustomUser.objects.all()
                                       ,widget=forms.Select(attrs={
                                          'class': "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500",
                                          'style': 'max-width: auto;',
                                      }), empty_label='-------------', to_field_name=  'username')
    # .values_list('name',flat=True)
    product= ModelChoiceField(queryset=Product.objects.all()
                                      ,widget=forms.Select(attrs={
                                          'class': "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500",
                                          'style': 'max-width: auto;',
                                          'name': 'productname'
                                      }), empty_label='-------------', to_field_name='name')
  

    class Meta:
        model = Tasks
        # fields = ['product','department','issuer', 'motivoEgreso', 'cantidad', 'date']
        fields = ['department','issuer', 'motivoEgreso']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user','')
        #product = kwargs.pop('name', None)
        product = kwargs.pop('product','')
        print('args are', args)
       # product = args[0].get('product',None)
        print('product is:', product)

        #print('product_ is:', product_)
        super(OutboundOrderForm, self).__init__(*args, **kwargs)

        print('self field products', self.fields['product'])

        #CustomPK._meta.pk.name
       # self.fields['cantidad'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-1/2 p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500'})
      #  self.fields['department'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-1/2 p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500'})

   
    
### OutboundDelivery Form
class OutboundDeliveryForm(forms.ModelForm):

    receptor = ModelChoiceField(queryset=CustomUser.objects.all()
                                       ,widget=forms.Select(attrs={
                                          'class': "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500",
                                          'style': 'max-width: auto;',
                                      }), empty_label='-------------', to_field_name=  'username')
    
    warehouse = forms.ModelChoiceField(queryset=Warehouses.objects.all()
                                      ,widget=forms.Select(attrs={
                                         'class': "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500",
                                         'style': 'max-width: auto;',
                                     }), empty_label='-------------', to_field_name='name')
    
    
    
    widgets = {
            'deliveryDate': forms.widgets.DateInput(attrs={'type': 'date'}),
         #   'cantidad': forms.Input(attrs={'class':"bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500"})
    }
    
    class Meta:
        model = Tasks
        # fields = ['product','department','issuer', 'motivoEgreso', 'cantidad', 'date',
        #           'receptor', 'cantidadEntregada', 'deliveryDate', 'warehouse']
        fields = ['department','issuer', 'motivoEgreso', 'date', 'receptor', 'warehouse']


    def __init__(self, *args, **kwargs):
        
        super(OutboundDeliveryForm, self).__init__(*args, **kwargs)

        print('products in form', self.initial['products'])
        print('args is', args)
        # self.fields['product'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-1/2 p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500',  'disabled':True})
        self.fields['department'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-1/2 p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500', 'disabled':True })

        self.fields['issuer'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-1/2 p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500',  'disabled':True})
        self.fields['date'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-1/2 p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500', 'disabled':True })

        # self.fields['cantidad'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-1/2 p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500',  'disabled':True})
        # self.fields['motivoEgreso'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-1/2 p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500', 'disabled':True })

        # #self.data.update({ 'product': self.instance.product })
        # self.fields['product'].widget.value_from_datadict = lambda *args: self.instance.product
        # self.fields['department'].widget.value_from_datadict = lambda *args: self.instance.department
        # self.fields['motivoEgreso'].widget.value_from_datadict = lambda *args: self.instance.motivoEgreso
        # self.fields['cantidad'].widget.value_from_datadict = lambda *args: self.instance.cantidad
        # self.fields['deliveryDate'].widget.value_from_datadict = lambda *args: self.instance.deliveryDate

    def save(self, *args, **kwargs):
      
        meal = super(OutboundDeliveryForm, self).save(*args, **kwargs)
        return meal