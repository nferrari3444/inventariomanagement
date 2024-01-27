from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.forms.utils import ValidationError
from django.forms import ModelChoiceField

from .models import (CustomUser, StockMovements, Product, DiffProducts , Warehouses)


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

### Inbound Form
class InboundForm(forms.ModelForm):
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

    # product= ModelChoiceField(queryset=Product.objects.all()
    #                                   ,widget=forms.Select(attrs={
    #                                       'class': "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500",
    #                                       'style': 'max-width: auto;',
                                          
    #                                       'id': 'productname'
    #                                   }), empty_label='-------------', to_field_name='product_id')
    
    class Meta:
        model = StockMovements
        fields = ['product','warehouse','motivoIngreso','receptor','image','cantidad','cantidadNeta']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user','')
        # product = kwargs.pop('product','')
        #self.product = args.pop('product','')
      
        print('args are', args)
       # barcode = args[0].get('barcode',None)
        
       # print('barcode is', barcode)

        super(InboundForm, self).__init__(*args, **kwargs)
        #self.fields['product']=forms.ModelChoiceField(queryset=Product.objects.values("name").values(),empty_label="Choose Product")
        # self.fields['warehouse'] = Warehouses.objects.all().values('name').distinct()
        self.fields['cantidad'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-1/2 p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500'})
        self.fields['cantidadNeta'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-1/2 p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500'})
        self.fields['motivoIngreso'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500'})
        self.fields['image'].required = False
        # make the 'name' field use a datalist to autocomplete
        # self.fields['product'].widget.attrs.update({'list': 'names'})
       
       

#self.fields['barcode'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500'})


       # self.fields['receptor'] = forms.ModelChoiceField(queryset=CustomUser.objects.all().values_list('username',flat=True), empty_label='Receptor')

        widgets = {
            'date': forms.widgets.DateInput(attrs={'type': 'date'}),
         #   'cantidad': forms.Input(attrs={'class':"bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500"})
        }
    def save(self, *args, **kwargs):
        product = args[0].get('product',None)
        print('product in save is', product)
        self.fields['product'] = product
        data = super(InboundForm, self).save(*args, **kwargs)
        return data
   

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
        model = StockMovements
        fields = ['product','department','issuer', 'motivoEgreso', 'cantidad', 'date']

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
        self.fields['cantidad'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-1/2 p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500'})
        self.fields['department'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-1/2 p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500'})

   
    
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
        model = StockMovements
        fields = ['product','department','issuer', 'motivoEgreso', 'cantidad', 'date',
                  'receptor', 'cantidadEntregada', 'deliveryDate', 'warehouse']


    def __init__(self, *args, **kwargs):
        
        super(OutboundDeliveryForm, self).__init__(*args, **kwargs)
        self.fields['product'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-1/2 p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500',  'disabled':True})
        self.fields['department'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-1/2 p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500', 'disabled':True })

        self.fields['issuer'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-1/2 p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500',  'disabled':True})
        self.fields['date'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-1/2 p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500', 'disabled':True })

        self.fields['cantidad'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-1/2 p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500',  'disabled':True})
        self.fields['motivoEgreso'].widget.attrs.update({'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 flex w-1/2 p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500', 'disabled':True })

        #self.data.update({ 'product': self.instance.product })
        self.fields['product'].widget.value_from_datadict = lambda *args: self.instance.product
        self.fields['department'].widget.value_from_datadict = lambda *args: self.instance.department
        self.fields['motivoEgreso'].widget.value_from_datadict = lambda *args: self.instance.motivoEgreso
        self.fields['cantidad'].widget.value_from_datadict = lambda *args: self.instance.cantidad
        self.fields['deliveryDate'].widget.value_from_datadict = lambda *args: self.instance.deliveryDate

    def save(self, *args, **kwargs):
      
        meal = super(OutboundOrderForm, self).save(*args, **kwargs)
        return meal