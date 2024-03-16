from typing import Any
from django.db.models.query import QuerySet
from django.contrib import messages
import numpy as np
import pandas as pd
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormView
from django.db.models import Avg, Count, Exists, OuterRef
from django.db.models import Count, F, Value, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)
import json
from django.template.loader import render_to_string
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
from datetime import datetime
from django.core import serializers
from django.views import generic
from annoying.functions import get_object_or_None
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.core.validators import validate_email
from django.core.exceptions import ValidationError, PermissionDenied
from .forms import SignUpForm , InboundForm, OutboundOrderForm, CotizationForm, OutboundDeliveryForm, InboundReceptionForm, TransferForm, TransferReceptionForm, CustomSetPasswordForm
from .models import CustomUser, StockMovements, DiffProducts, Product, WarehousesProduct, Tasks, Cotization
from django.core.cache import cache
from django.utils.http import urlsafe_base64_encode
from django.core.mail import send_mail, BadHeaderError
from django.contrib.auth.views import PasswordResetView, PasswordContextMixin
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.contrib.messages.views import SuccessMessageMixin
import openpyxl

# Create your views here.

class UserSignUpView(CreateView):
    model = CustomUser
    form_class = SignUpForm
    template_name = 'registration/signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'teacher'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('/')


@login_required
def index(request):
    return render(request, 'index.html')

def Register(request):

    if request.method == 'POST':
        username = request.POST.get('username','username')
        email = request.POST.get('email','email')

        try:
            validate_email(email)
        except ValidationError as e:
            messages.error(request, "Se debe agregar usuario y contraseña para Loguearse", extra_tags='login')


        password = request.POST.get('password', 'password')

        newUser = CustomUser.objects.create_user(username=username, email=email, password=password)

        newUser.save()

        return render(request, 'registration/login.html')
    
    else:
        return render(request, 'registration/register.html')
    
class PasswordResetConfirmView(PasswordContextMixin, FormView):
    form_class= CustomSetPasswordForm

def Login(request):
    
    page ='login'
    print('login view')
    if request.method == 'POST':
        email = request.POST.get('email','email')

        print('email is {}'.format(email))
        
        try:
            validate_email(email)
        except ValidationError as e:
            messages.error(request, 'El correo debe tener @', extra_tags='login')
            return render(request, 'registration/login.html')
        
        #username = CustomUser.objects.get(email=email)
        username = CustomUser.objects.filter(email=email).values_list('username', flat=True)
      #  print('username get is', username)
        print('username values_list is', username)

        print('request user is ', request.user)    
        password = request.POST.get('password','password')

        if len(username) == 0 | len(password) == 0:
            messages.error(request, "Se debe agregar usuario y contraseña para Loguearse", extra_tags='login')
            return render(request, 'registration/login.html')
        
        user = authenticate(request, email=  email , password=password)

        print('request user after auth is ', request.user)  
        print('user auth is ', user)  
        if user is not None:
            login(request, user)
            return redirect('/')
        
        else:
            messages.info(request, 'Usuario no existe. Se necesita dar de alta nuevo usuario')
            return render(request, 'registration/login.html')

    else:
        context = {'page' : page}
        return render(request, 'registration/login.html', context)
    

def Logout(request):
  
    logout(request)

    return redirect('/')


def getProducts(request):
 
    if cache.get('all') is not None:
        objects = cache.get('all')

        print('data in cache', objects)
    else:
        objects = Product.objects.all()
        categories = Product.objects.all().values('category').distinct()
        suppliers = Product.objects.all().values('supplier').distinct()
        warehouses = WarehousesProduct.objects.all().values('name').distinct()

        cache.set('products', objects)
        cache.set('categories', categories)
        cache.set('suppliers',suppliers) 
        cache.set('warehouses',warehouses)



    product = Product.objects.filter()
    product_data = Product.objects.values_list('name','product_id','internalCode')
  #  data = serializers.serialize('json', product_data, fields=('name','barcode', 'internalCode'))
    internalCodeJson = {product[2]: product[1] for product in product_data}

    productJson = {product[0]: product[1] for product in product_data}


    return JsonResponse({'products': productJson, 'codes':internalCodeJson}) #, 'warehouses': warehouses_json_data,'categories':  categories_json_data, 'supplier': suppliers_json_data})


def getProductsNames(request):
    
    print('autocomplete', request.GET.get('term'))
    if 'term' in request.GET:
        searchvalue = request.GET.get('term')
        if searchvalue.isdigit() == False:

            qs = Product.objects.filter(name__istartswith=searchvalue)
            titles = []
        
            for product in qs:
                titles.append(product.name)
         
            print(titles)       
            titles = list(set(titles)) 
            return JsonResponse(titles, safe=False)
        
        else:
            qs = Product.objects.filter(internalCode__istartswith= searchvalue)
            codes = []
        
            for product in qs:
                print('product in autocomplete is',product)
                print('internal code in autocomplete is', product.internalCode)
                codes.append(str(product.internalCode))
         
            print(codes)      
            codes = list(set(codes))  
            return JsonResponse(codes,safe=False)
            

def getProduct(request,productId):
    product = Product.objects.get(product_id=productId)
        
    print('product is', product)
    product_data = Product.objects.filter(product_id=productId).values_list('barcode','internalCode', 'name','category','supplier','quantity')
    
    print('product_data is', product_data)

    return JsonResponse({'product': list(product_data)})

def getProductWarehouse(request, productId, warehouse):

    print('warehouse from template is', warehouse)

    #Warehouse = Warehouses.objects.filter(name=warehouse)
    product = Product.objects.filter(product_id=productId)

    print('product has offer', product[0].hasOffer)
    if product[0].hasOffer != None:
        product_name = product[0].name
        quantity = product[0].quantity
        quantityOffer = product[0].quantityOffer
        stockSecurity = product[0].stockSecurity

        if quantity - quantityOffer < stockSecurity * 1.1:
            response =  JsonResponse({'error': 'El producto {} tiene cotización de Oferta y se encuentra cerca del Stock de Seguridad. El stock se encuentra reservado '.format(product_name)})
            response.status_code = 403
            return response
        else:
            response =  JsonResponse({'error': 'El producto {} tiene cotización de Oferta y se encuentra cerca del Stock de Seguridad. El stock se encuentra reservado '.format(product_name)})
            response.status_code = 403
            return response

        print('el producto está en Oferta de cotizacion')
    try:
        product = Product.objects.get(product_id=productId) #, warehouse= Warehouses.objects.get(name=warehouse))
        #product = getProductWarehouse.objects.get(Product, name= warehouse)
        print('product is', product)
        #product_data = Product.objects.filter(product_id=productId, warehouse= Warehouses.objects.get(name=warehouse)).values_list('barcode','internalCode', 'name','warehouse','location','category','supplier','quantity', 'hasOffer')
        product_warehouse = WarehousesProduct.objects.filter(Product, name= warehouse).values_list('barcode','internalCode', 'name','warehouse','location','category','supplier','quantity', 'hasOffer')
        #print('product_data is', product_data)
        print('product_data is', product)

        return JsonResponse({'product': list(product)})
    except Product.DoesNotExist:
        print('da error en la vista')
        response =  JsonResponse({'error': 'El Producto ingresado no se encuentra en el Deposito {} '.format(warehouse)})
        response.status_code = 403
        return response
    
    


@login_required
def transferView(request):

    productNames = Product.objects.values_list('name', flat=True)
    print('extra_Field_count', request.POST.get('extra_field_count'))
    numberOfProducts = request.POST.get('extra_field_count')
    print('number of products in Inbound View is {}'.format(numberOfProducts))
    transferencia = StockMovements()
    # if this is a POST request we need to process the form data
    if request.method == "POST":
        # # create a form instance and populate it with data from the request:
        form = TransferForm(request.POST, user = request.user, extra = request.POST.get('extra_field_count'))
        # # check whether it's valid:
        print('form is valid', form.is_valid())
       
        if form.is_valid():
      
            date  =   datetime.today().strftime('%Y-%m-%d')
        
            receptor = form.cleaned_data['receptor']
            warehouse_out = form.cleaned_data['warehouse']
            solicitante = request.user
            department = form.cleaned_data['department']
            motivoIngreso = 'Transferencia'
            # motivoIngreso = form.cleaned_data['motivoIngreso']
            actionType = 'Transferencia'
       

            print('number of Products in form is {}'.format(numberOfProducts))
            datalist = []
            
            products_list = [form.cleaned_data['product_{}'.format(i)] for i in range(0,int(numberOfProducts))]
            print('products_list is {}'.format(products_list))
            print('products_list exists:')
            
            print('Product that not exist in database are:')    

            task = Tasks.objects.create(date= date, receptor= receptor, warehouse= warehouse_out, issuer=solicitante,
                                        motivoIngreso=motivoIngreso,  actionType=actionType, department=department)
            
            for i in range(0,int(numberOfProducts)):

                product = form.cleaned_data['product_{}'.format(i)]
                print('product in inbound view is {}'.format(product))
                
                # if Product.objects.filter(name__in=product, warehouse=warehouse_out).exists() != True:
                #     messages.error(request, 'El producto seleccionado {} no se encuentra en el deposito {}. Dar de alta el producto en el deposito para continuar'.format(product,warehouse_out), extra_tags='transfer')
                #     return redirect('/transfer/')
                    
                productdb = Product.objects.get(name= product, warehouse= warehouse_out)
                
              
                quantity = form.cleaned_data['cantidad_{}'.format(i)]

                print('product is:', product)
                print('quantity is:', quantity)
                print('productId is:', productdb.product_id)
                #productdb = Product.objects.get(name= newproduct.product.name)

                productToUpdate= Product.objects.filter(product_id= productdb.product_id, warehouse=warehouse_out)
        
                print('productToUpdate is:', productToUpdate)

                productToUpdate.update(quantity = F('quantity') - quantity  )
        

                newProduct = StockMovements(product = productdb, 
                            actionType = actionType,
                                        cantidad= quantity, task = task )
            

                barcode = productdb.barcode
                internalCode = productdb.internalCode
                category =  productdb.category
                location = 'Transit'
                supplier = productdb.supplier
                warehouse = Warehouses.objects.get(name='En Transito') 
                deltaQuantity = 0
                stockSecurity = 0
                inTransit = False
                productInTransit = Product.objects.create(name= product, warehouse= warehouse,
                            barcode= barcode, quantity = quantity, internalCode= internalCode, category= category,
                            location = location, supplier = supplier , deltaQuantity= deltaQuantity,
                            stockSecurity = stockSecurity, inTransit=inTransit)
            

                datalist.append(newProduct)

           
            
          
            StockMovements.objects.bulk_create(datalist)     

            send_mail(
                subject='Transferencia de Productos entre Depositos',
                message= 'Transferencia de {} productos a depósito {}'.format(numberOfProducts,warehouse),
                from_email = settings.EMAIL_HOST_USER,
                recipient_list=[receptor],
                fail_silently=False,
                auth_user=None,
                auth_password=None,
                connection=None,
                html_message=None
            )
       
            return redirect('/tasks/')
            #return HttpResponseRedirect("/inbound/")

    # if a GET (or any other method) we'll create a blank form
    else:
        
        form = TransferForm(user=request.user)

    return render(request, "transfer.html", {"form": form}) #, "products" :productNames})

@login_required
def transferReceptionView(request, requested_id):

    pendingTask = get_object_or_None(Tasks, pk=requested_id)
    print('request is:', request.method)
    print('request product data', request.POST.get('product_0'))
    product = request.POST.get('product')
    issuer = request.POST.get('issuer')
    #productsToReceive = pendingTask.stockmovements_set.all().values()
    # pendingTask:
    products = pendingTask.stockmovements_set.all()
    #task = Tasks.objects.filter(task_id = requested_id)
    tasks = Tasks.objects.filter(task_id=requested_id, actionType='Transferencia').prefetch_related('stockmovements_set')

    numberOfProducts = request.POST.get('extra_field_count')
    print('number Of Produtos in Inbound Reception View is {}'.format(numberOfProducts))
     # if this is a POST request we need to process the form data
    if request.method == "POST":
        
        form = TransferReceptionForm(request.POST, instance= pendingTask, extra= request.POST.get('extra_field_count'))

        print('form is valid', form.is_valid())
      #  print('form is', form)
        print('form fields are', form.cleaned_data)

        # check whether it's valid:
        if form.is_valid():
            print('el form es valido')
           #product = form.cleaned_data['product']
           # date  =   form.cleaned_data['date']
            
           # print(product)
           # print(date)
            department = form.cleaned_data['department']
            issuer = form.cleaned_data['issuer']
            receptor = form.cleaned_data['receptor']
            warehouse = form.cleaned_data['warehouse']
            actionType = 'Confirma Transferencia'
            observations = form.cleaned_data['observations']
            deliveryDate = datetime.now().date()
            datalist = []
            # task = Tasks.objects.create(date= date, receptor= receptor, warehouse= warehouse, issuer= issuer,
            #                             motivoIngreso=motivoIngreso,  actionType=actionType, department=department)
            
            taskToUpdate = Tasks.objects.filter(task_id=requested_id)
            taskToUpdate.update(status='Confirmed', observations=observations, deliveryDate=deliveryDate)
            
            taskupdated = Tasks.objects.filter(task_id = requested_id).values_list('receptor', 'issuer','status', 'motivoIngreso','motivoEgreso','warehouse','actionType')
            print('taskupdated in view is ', taskupdated)
            task = Tasks.objects.get(task_id=requested_id)
            warehouseInTransit = Warehouses.objects.get(name='En Transito') 
            for i , product in enumerate(products):
                form.fields['producto_{}'.format(i)] = product.product.name
                form.fields['cantidad_{}'.format(i)] = product.cantidad
                netQuantity = form.cleaned_data['cantidadNeta_{}'.format(i)]
                
                quantity = form.fields['cantidad_{}'.format(i)]
                diffQuantity = int(quantity) - int(netQuantity)
                productdb = Product.objects.filter(name= product.product.name, warehouse=warehouse)
                print('productdb is', productdb)
                # productToUpdate= Product.objects.filter(product_id= newproduct.product_id, warehouse=warehouse)
                productToUpdate= Product.objects.filter(name= product.product.name, warehouse=warehouse)
                # productToUpdate = get_object_or_None(Product, name=product.product.name, warehouse=warehouse)
                print('productToUPdate is', productToUpdate)
                
                if productToUpdate.exists():    
                    product_data = Product.objects.get(name= product.product.name, warehouse=warehouse)
                    # print('product line 273 is:', product)
                    productToUpdate= Product.objects.filter(name= product.product.name, warehouse=warehouse)
                    productToUpdate.update(quantity = F('quantity') + netQuantity, deltaQuantity = F('deltaQuantity') - diffQuantity ,inTransit=False )
                    newProduct = StockMovements(product = product_data, 
                             actionType = actionType,
                                         cantidad= quantity, cantidadNeta=netQuantity, task = task )
                
                    datalist.append(newProduct)
                else:
                    productdb = Product.objects.filter(name= product.product.name).first()
                    barcode = productdb.barcode
                    internalCode = productdb.internalCode
                    category =  productdb.category
                    location = productdb.location
                    supplier = productdb.supplier
                    warehouse = Warehouses.objects.get(name=warehouse) 
                    deltaQuantity = 0
                    stockSecurity =  np.ceil(quantity * 0.3) #   productdb.stockSecurity
                    inTransit = False
                    newProductInDeposit = Product.objects.create(name=product.product.name, warehouse=warehouse,
                                barcode= barcode, quantity = quantity, internalCode= internalCode, category= category,
                                location = location, supplier = supplier , deltaQuantity= deltaQuantity,
                                stockSecurity = stockSecurity, inTransit=inTransit)
                       
                    # newProduct.save()

                    newProductMovement = StockMovements(product = newProductInDeposit, 
                             actionType = actionType,
                                         cantidad= quantity, cantidadNeta=netQuantity, task = task )
                
                    datalist.append(newProductMovement)
                    
                 
                
                # productToDelete = Product.objects.filter(product_id= newproduct.product_id, warehouse='InTransit')
                productToDelete = Product.objects.filter(name= product.product.name, warehouse= warehouseInTransit)

                print('productToUpdate is:', productToUpdate)

             
                productToDelete.delete()

                # newProduct = StockMovements(product = productToUpdate, 
                #              actionType = actionType,
                #                          cantidad= quantity, cantidadNeta=netQuantity, task = task )
                
                # datalist.append(newProduct)
            
            print('new_product is:', datalist)

            StockMovements.objects.bulk_create(datalist)     


            return redirect('/tasks/')
            
    else:
       # form = OutboundOrderForm()
        form = TransferReceptionForm(instance= pendingTask , 
                                    initial={"task_id": requested_id })
        #form.task.queryset = Tasks.objects.filter(task_id = requested_id) 
        
    return render(request, "transferReception.html", {"form": form, 'task_id': requested_id , "tasks": tasks}) #, "numberOfProducts": len(productsToReceive)})

@login_required
def inboundView(request):

    print(request.user.role)
    productNames = Product.objects.values_list('name', flat=True)
    print('extra_Field_count', request.POST.get('extra_field_count'))
    numberOfProducts = request.POST.get('extra_field_count')
    print('number of products in Inbound View is {}'.format(numberOfProducts))
    nuevoIngreso = StockMovements()
    # if this is a POST request we need to process the form data
    if request.method == "POST":
        # # create a form instance and populate it with data from the request:
        form = InboundForm(request.POST, user = request.user, extra = request.POST.get('extra_field_count'))
        # # check whether it's valid:
        print('form is valid', form.is_valid())
       
        if form.is_valid():
        #     # process the data in form.cleaned_data as 
        #     product = form.cleaned_data['product']
            date  =   datetime.today().strftime('%Y-%m-%d')
           # print('form is:', form)

        #     print(product)
        #     print(date)
            
            receptor = form.cleaned_data['receptor']
            warehouse = form.cleaned_data['warehouse']
            solicitante =  request.user
            department = form.cleaned_data['department']
        #     cantidad = form.cleaned_data['cantidad']
        #     cantidadNeta = form.cleaned_data['cantidadNeta']
        #     deltaDiff =  cantidadNeta - cantidad
            motivoIngreso = form.cleaned_data['motivoIngreso']
            actionType = 'Nuevo Ingreso'
          #  product = form.cleaned_data['product_23']
         #   print('product_23 is {}'.format(product))

            print('number of Products in form is {}'.format(numberOfProducts))
            datalist = []
            task = Tasks.objects.create(date= date, receptor= receptor, warehouse= warehouse, issuer=solicitante,
                                        motivoIngreso=motivoIngreso,  actionType=actionType, department=department)
            
            for i in range(0,int(numberOfProducts)):

                product = form.cleaned_data['product_{}'.format(i)]
                print('product in inbound view is {}'.format(product))
                quantity = form.cleaned_data['cantidad_{}'.format(i)]
                if Product.objects.filter(name=product, warehouse=warehouse).exists():
                    print('warehouse in line 430 is', warehouse)
                    print('product in line 431 is', product)

                    newproduct = Product.objects.get(name= product, warehouse=warehouse)
                    
                    # nuevoIngreso.barcode = form.cleaned_data['barcode_{}'.format(i)]
                    # nuevoIngreso.internalCode = form.cleaned_data['internalCode_{}'.format(i)]
                    

                    print('product is:', product)
                    print('quantity is:', quantity)

                    newProduct = StockMovements(product = newproduct, 
                             actionType = actionType,
                                         cantidad= quantity, task = task )
                
                    datalist.append(newProduct)
                
                else:
                    stockSecurity = np.ceil(quantity * 0.3)
                    warehouse_obj = Warehouses.objects.get(name=warehouse)
                    barcode = form.cleaned_data['barcode_{}'.format(i)]
                    internalCode = form.cleaned_data['internalCode_{}'.format(i)]
                    cantidad = form.cleaned_data['cantidad_{}'.format(i)]
                    newproduct_db = Product.objects.create(name=product, barcode=barcode,internalCode=internalCode,quantity=0, 
                                           warehouse= warehouse_obj, deltaQuantity=0, stockSecurity= stockSecurity, inTransit=True)

                    newproduct_db.save()

                    newProduct = StockMovements(product = newproduct_db, 
                             actionType = actionType,
                                         cantidad= cantidad, task = task )
                    
                    

                    datalist.append(newProduct)
               
            print('new_product is:', datalist)

            StockMovements.objects.bulk_create(datalist)

            send_mail(
                subject='Nueva Solicitud de Ingreso de Materiales',
                message= 'Solicitud de Recepción de {} productos a depósito {} por motivo de {}'.format(numberOfProducts,warehouse,motivoIngreso),
                from_email = settings.EMAIL_HOST_USER,
                recipient_list=[receptor],
                fail_silently=False,
                auth_user=None,
                auth_password=None,
                connection=None,
                html_message=None
            )
        
        
            return redirect('/tasks/')
            #return HttpResponseRedirect("/inbound/")

    # if a GET (or any other method) we'll create a blank form
    else:
        
        form = InboundForm(user=request.user)

    return render(request, "inbound.html", {"form": form}) #, "products" :productNames})

@login_required
def inboundReceptionView(request, requested_id):

    pendingTask = get_object_or_None(Tasks, pk=requested_id)
    print('request is:', request.method)
    print('request product data', request.POST.get('product_0'))
    product = request.POST.get('product')
    issuer = request.POST.get('issuer')
    #productsToReceive = pendingTask.stockmovements_set.all().values()
    if pendingTask:
        products = pendingTask.stockmovements_set.all()
    #task = Tasks.objects.filter(task_id = requested_id)
    tasks = Tasks.objects.filter(task_id=requested_id, actionType='Nuevo Ingreso').prefetch_related('stockmovements_set')

    numberOfProducts = request.POST.get('extra_field_count')
    print('number Of Produtos in Inbound Reception View is {}'.format(numberOfProducts))
     # if this is a POST request we need to process the form data
    if request.method == "POST":
        
        form = InboundReceptionForm(request.POST, instance= pendingTask, extra= request.POST.get('extra_field_count'))

        print('form is valid', form.is_valid())
      #  print('form is', form)
        print('form fields are', form.cleaned_data)

        # check whether it's valid:
        if form.is_valid():
            print('el form es valido')
           #product = form.cleaned_data['product']
           # date  =   form.cleaned_data['date']
            
           # print(product)
           # print(date)
            department = form.cleaned_data['department']
            issuer = form.cleaned_data['issuer']
            receptor = form.cleaned_data['receptor']
            warehouse = form.cleaned_data['warehouse']
            actionType = 'Confirma Ingreso'
            motivoIngreso = form.cleaned_data['motivoIngreso']
            observations = form.cleaned_data['observations']
            deliveryDate = datetime.now().date()
            
            # StockMovements.objects.create(product = product, date=date, department=department,
            #                             issuer=issuer, actionType = actionType, cantidad=cantidad,
            #                             motivoEgreso=motivoIngreso,status='Pending')
            
            datalist = []
            # task = Tasks.objects.create(date= date, receptor= receptor, warehouse= warehouse, issuer= issuer,
            #                             motivoIngreso=motivoIngreso,  actionType=actionType, department=department)
            
            taskToUpdate = Tasks.objects.filter(task_id=requested_id)
            taskToUpdate.update(status='Confirmed', observations=observations, deliveryDate=deliveryDate)
            
            taskupdated = Tasks.objects.filter(task_id = requested_id).values_list('receptor', 'issuer','status', 'motivoIngreso','motivoEgreso','warehouse','actionType')
            print('taskupdated in view is ', taskupdated)
            task = Tasks.objects.get(task_id=requested_id)
            
            for i , product in enumerate(products):
                form.fields['producto_{}'.format(i)] = product.product.name
                form.fields['cantidad_{}'.format(i)] = product.cantidad
                netQuantity = form.cleaned_data['cantidadNeta_{}'.format(i)]
                
                quantity = form.fields['cantidad_{}'.format(i)]
                diffQuantity = int(quantity) - int(netQuantity)
                newproduct = Product.objects.get(name= product.product.name, warehouse=warehouse)

                productToUpdate= Product.objects.filter(product_id= newproduct.product_id, warehouse=warehouse)
            
                print('productToUpdate is:', productToUpdate)

                productToUpdate.update(quantity = F('quantity') + netQuantity, deltaQuantity = F('deltaQuantity') - diffQuantity , inTransit=False )
            

                newProduct = StockMovements(product = newproduct, 
                             actionType = actionType,
                                         cantidad= quantity, cantidadNeta=netQuantity, task = task )
                

                if diffQuantity > 0 and motivoIngreso in('Importación','Compra en Plaza'):
                    if DiffProducts.objects.filter(product=newproduct, warehouse= warehouse).exists():
                        
                        DiffProducts.objects.filter(product=newproduct, warehouse=warehouse).update(totalPurchase= F('totalPurchase') + quantity, totalQuantity= F('totalQuantity') + netQuantity, productDiff= F('productDiff') + diffQuantity)

                    else:
                        
                        DiffProducts.objects.create(product=newproduct, warehouse=warehouse, totalPurchase=quantity, totalQuantity= netQuantity, productDiff= diffQuantity)
                
                datalist.append(newProduct)
            print('new_product is:', datalist)

            StockMovements.objects.bulk_create(datalist)     


            return redirect('/tasks/')
            
    else:
       # form = OutboundOrderForm()
        form = InboundReceptionForm(instance= pendingTask ,
                                    initial={"task_id": requested_id })
        #form.task.queryset = Tasks.objects.filter(task_id = requested_id) 
        
    return render(request, "inboundReception.html", {"form": form, 'task_id': requested_id , "tasks": tasks}) #, "numberOfProducts": len(productsToReceive)})


@login_required
def inboundConfirmedView(request, requested_id):
   # pendingRequest = get_object_or_None(StockMovements, pk=requested_id)
    #print('pendingRequest product is:', pendingRequest.product)
    # confirmedTask = get_object_or_None(Tasks, pk=requested_id)
    confirmedTask = Tasks.objects.filter(task_id=requested_id, status='Confirmed')

    return render(request, 'inboundConfirmed.html', { 'task': confirmedTask[0] })

@login_required
def transferConfirmedView(request, requested_id):
   # pendingRequest = get_object_or_None(StockMovements, pk=requested_id)
    #print('pendingRequest product is:', pendingRequest.product)
    # confirmedTask = get_object_or_None(Tasks, pk=requested_id)
    confirmedTask = Tasks.objects.filter(task_id=requested_id, status='Confirmed')

    return render(request, 'transferConfirmed.html', { 'task': confirmedTask[0] })


@login_required
def outboundOrderView(request):
    print('request is:', request.method)
    print('request product data', request.POST.get('product'))
    product = request.POST.get('product')
    #issuer = request.POST.get('issuer')

    print('request user is ', request.user)
    context = {}
    numberOfProducts = request.POST.get('extra_field_count')

     # if this is a POST request we need to process the form data
    if request.method == "POST":
        
        form = OutboundOrderForm(request.POST, user = request.user, extra = request.POST.get('extra_field_count'))

        print('request POST FORM')
        print(request.POST)
        if form.is_valid():
            print('form is valid', form.is_valid())
            #print('form is', form)
            date  =   datetime.today().strftime('%Y-%m-%d')
           # print('form is:', form)

        #     print(product)
        #     print(date)
            
            receptor = form.cleaned_data['receptor']
            warehouse = form.cleaned_data['warehouse']
            # solicitante = form.cleaned_data['issuer']
            department = form.cleaned_data['department']
            #     cantidad = form.cleaned_data['cantidad']
            #     cantidadNeta = form.cleaned_data['cantidadNeta']
            #     deltaDiff =  cantidadNeta - cantidad
            motivoEgreso = form.cleaned_data['motivoEgreso']
            actionType = 'Nuevo Egreso'
            #form.fields['issuer'] = request.user
            solicitante = request.user
            #  product = form.cleaned_data['product_23']
            #   print('product_23 is {}'.format(product))

            print('number of Products in form is {}'.format(numberOfProducts))
            datalist = []
            task = Tasks.objects.create(date= date, receptor= receptor, warehouse= warehouse, issuer=solicitante,
                                        motivoEgreso=motivoEgreso,  actionType=actionType, department=department)
            
            print('form cleaned data', form.cleaned_data)
            for i in range(0,int(numberOfProducts) ):


                product = form.cleaned_data['producto_{}'.format(i)]
                newproduct = Product.objects.get(name= product, warehouse=warehouse)
                
                # nuevoIngreso.barcode = form.cleaned_data['barcode_{}'.format(i)]
                # nuevoIngreso.internalCode = form.cleaned_data['internalCode_{}'.format(i)]
                quantity = form.cleaned_data['cantidad_{}'.format(i)]

                print('product is:', product)
                print('quantity is:', quantity)
                newProduct = StockMovements()
                newProduct.product = newproduct
                newProduct.actionType = actionType
                newProduct.cantidad = quantity
                newProduct.task = task
#               newProduct = StockMovements(product = newproduct, 
 #                            actionType = actionType,
   #                                      cantidad= quantity, task = task )
           
                datalist.append(newProduct)
                print('new_product is:', datalist)

            StockMovements.objects.bulk_create(datalist)

            send_mail(
                subject='Nueva Solicitud de Egreso de Materiales',
                message= 'Solicitud de Egreso por {} productos a depósito {} por motivo de {}. La solicitud fue ingresada por {}'.format(numberOfProducts,warehouse,motivoEgreso,solicitante),
                from_email = settings.EMAIL_HOST_USER,
                recipient_list=[receptor],
                fail_silently=False,
                auth_user=None,
                auth_password=None,
                connection=None,
                html_message=None
            )
        
            return redirect('/tasks/')
        else:

        #    context['form'] = form
            form = OutboundOrderForm(request.POST, user = request.user, extra = request.POST.get('extra_field_count'))

            return render(request, "outboundOrder.html", {"form": form})

    else:
        form = OutboundOrderForm(user = request.user)
        #context['form'] = OutboundOrderForm(user = request.user)
    
    return render(request, "outboundOrder.html", {"form": form})

class TaskListView(LoginRequiredMixin, generic.ListView):
    template_name = 'tasks.html'
    model = Tasks    

    def get_queryset(self) -> QuerySet[Any]:
        self.tasks = Tasks.objects.all() #filter(status='Pending') # , actionType='Nueva Solicitud')

        return self.tasks
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(TaskListView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        context['tasks'] = self.tasks
        return context 
    
class StockListView(LoginRequiredMixin, generic.ListView):
    paginate_by = 10
    model = Product
    
    template_name = 'stock.html'
    
    print('llega aca con el checkbox')
   

    def get_context_data(self, *args, **kwargs):
        # Call the base implementation first to get the context
        #products_obj = Product.objects.all().values()
        context = super(StockListView, self).get_context_data(*args, **kwargs)

        warehouse = self.request.GET.get('warehouse',None)
        print('warehouse is', warehouse)
        supplier = self.request.GET.get('supplier',None)
        category = self.request.GET.get('category',None)

        if category:
            category_filter = True
            categoryList = [category]
        else:
            categoryList = Product.objects.all().values('category').distinct()

        if supplier:
            supplier_filter = True
            supplierList = [supplier]
        
        else:
            supplierList = Product.objects.all().values('supplier').distinct()

        if warehouse:
            warehouse = Warehouses.objects.get(name=warehouse)
            warehouseList = Warehouses.objects.get(name=warehouse)
            context.update({'products' : Product.objects.select_related('warehouse').filter(warehouse=warehouse, category ='Insumos', inTransit=False)}) #, supplier ='De Salt') 
        else:
            warehouseList = Warehouses.objects.all()
            
            #context['products'] = Product.objects.select_related('warehouse').filter(category ='Insumos') #, supplier ='De Salt') 
        context['products'] = Product.objects.all().select_related('warehouse').filter(inTransit=False) #.filter(category__in=categoryList, supplier__in=supplierList) 
        print('categoryList', categoryList)
        print('args', args)
        print('kwargs in get_context_data', kwargs)
        # Create any data and add it to the context
        
     
        #Product.objects.all().values('name','barcode','internalCode','location',
        #                                            'warehouse', 'category', 'supplier', 'quantity')

        context['productList'] = Product.objects.all().values('name').distinct()
        context['categoryList'] = Product.objects.all().values('category').distinct()
        context['supplierList'] = Product.objects.all().values('supplier').distinct()
        context['warehouseList'] = Warehouses.objects.all().values('name').distinct()
        
        print('context in get_context_data', context)
        return context 
       
# def stockProducts(request):
#     warehouse = request.GET.get('warehouse',None)
#     category = request.GET.get('category',None)
#     supplier = request.GET.get('supplier',None)

#     product = request.GET.get('product',None)
#     print('warehouse is', warehouse)
#     checkbox= request.GET.get('checkbox',None)

#     if category and category != 'Total Categorias':
#         category_filter = True
#         categoryList = [category]
#     else:
#         categoryList = Product.objects.all().values('category').distinct()

#     if supplier and supplier != 'Total Proveedores':
#         supplier_filter = True
#         supplierList = [supplier]
    
#     else:
#         supplierList = Product.objects.all().values('supplier').distinct()

#     if warehouse and warehouse != 'Total Depositos':
#         warehouse = Warehouses.objects.get(name=warehouse)
#         filter_data = Product.objects.select_related('warehouse').filter(warehouse=warehouse, category__in =categoryList, supplier__in=supplierList, inTransit=False) 

#         paginator = Paginator(filter_data, 20) # 6 employees per page

#         page_num = request.GET.get('page')

#         try:
#             page_obj = paginator.page(page_num)
#         except PageNotAnInteger:
#             # if page is not an integer, deliver the first page
#             page_obj = paginator.page(1)
#         except EmptyPage:
#             # if the page is out of range, deliver the last page
#             page_obj = paginator.page(paginator.num_pages)

#         # Se sustituye filter_data por page_obj
#         # context = {'products' : filter_data}
#         context = {'page_obj' : page_obj}

#         productList = Product.objects.all().values('name').distinct()
#         categoryList = Product.objects.all().values('category').distinct()
#         supplierList = Product.objects.all().values('supplier').distinct()
#         warehouseList = Warehouses.objects.all().values('name').distinct()

#         return render(request, 'stock.html', {'productList' : productList, 'supplierList':supplierList, 'warehouseList':warehouseList,   'categoryList':categoryList,  'page_obj': page_obj})

    
#     else:
#         filter_data = Product.objects.select_related('warehouse').filter(category__in =categoryList, supplier__in=supplierList, inTransit=False) 

#     paginator = Paginator(filter_data, 20) # 6 employees per page

#     page_num = request.GET.get('page')
    
#     try:
#         page_obj = paginator.page(page_num)
#     except PageNotAnInteger:
#         # if page is not an integer, deliver the first page
#         page_obj = paginator.page(1)
#     except EmptyPage:
#         # if the page is out of range, deliver the last page
#         page_obj = paginator.page(paginator.num_pages)

#     # Se sustituye filter_data por page_obj
#     # context = {'products' : filter_data}
#     context = {'page_obj' : page_obj}

#     productList = Product.objects.all().values('name').distinct()
#     categoryList = Product.objects.all().values('category').distinct()
#     supplierList = Product.objects.all().values('supplier').distinct()
#     warehouseList = Warehouses.objects.all().values('name').distinct()
    
#     return render(request, 'stock.html', {'productList' : productList, 'supplierList':supplierList, 'warehouseList':warehouseList,   'categoryList':categoryList,  'page_obj': page_obj})


def filterProducts(request):
    
    
    
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    page_num = request.GET.get('page')
    if is_ajax:
        print('is_ajax', is_ajax)
        data = dict()
        print('llega acaaaaa')
        warehouse = request.GET.get('warehouse',None)
        category = request.GET.get('category',None)
        supplier = request.GET.get('supplier',None)
    
        product = request.GET.get('product',None)
    
        checkbox= request.GET.get('checkbox',None)

        if checkbox:
            products = Product.objects.select_related('warehouse').filter(inTransit=False)  
            data = dict() 
            product_dict  = {'page_obj' : products}
            data['html_table'] =  render_to_string('inject_table.html',
                            context = product_dict,
                        request = request
                            )

            return JsonResponse(data)
    
        print('product is',product)
        if product:
            products = Product.objects.filter(name=product, inTransit=False)
            context = {'page_obj' : products}
            data['html_table'] =  render_to_string('inject_table.html',
                                context,
                                request = request
                                )
        
            return JsonResponse(data)

        if category and category != 'Total Categorias':
            category_filter = True
            categoryList = [category]
        else:
            categoryList = Product.objects.all().values('category').distinct()

        if supplier and supplier != 'Total Proveedores':
            supplier_filter = True
            supplierList = [supplier]
        
        else:
            supplierList = Product.objects.all().values('supplier').distinct()

    
        print('warehouse is', warehouse)
        print('category is', categoryList)
        print('supplier is', supplierList)

        if warehouse and warehouse != 'Total Depositos':
            warehouse = Warehouses.objects.get(name=warehouse)
            filter_data = Product.objects.select_related('warehouse').filter(warehouse=warehouse, category__in =categoryList, supplier__in=supplierList, inTransit=False) 
        else:
            filter_data = Product.objects.select_related('warehouse').filter(category__in =categoryList, supplier__in=supplierList, inTransit=False) 

    # data = serializers.serialize("json", Product.objects.filter(warehouse=warehouse, category=category, supplier=supplier).select_related('warehouse') )
        
        paginator = Paginator(filter_data, 20) # 6 employees per page

        page_num = request.GET.get('page')
        try:
            page_obj = paginator.page(page_num)
        except PageNotAnInteger:
            # if page is not an integer, deliver the first page
            page_obj = paginator.page(1)
        except EmptyPage:
            # if the page is out of range, deliver the last page
            page_obj = paginator.page(paginator.num_pages)

        # Se sustituye filter_data por page_obj
        # context = {'products' : filter_data}
        context = {'page_obj' : page_obj}
    
        productList = Product.objects.all().values('name').distinct()
        categoryList = Product.objects.all().values('category').distinct()
        supplierList = Product.objects.all().values('supplier').distinct()
        warehouseList = Warehouses.objects.all().values('name').distinct()
        
       # return render(request, 'stock.html',{'productList' : productList, 'supplierList':supplierList, 'warehouseList':warehouseList,   'categoryList':categoryList,  'page_obj': page_obj})
    
        data['html_table'] =  render_to_string('inject_table.html',
                                 context,
                                 request = request
                                 )
        
        #return render(request, 'stock.html', {'page_obj': page_obj})
        return JsonResponse(data)

        #return render(request, 'stock.html', {'productList' : productList, 'supplierList':supplierList, 'warehouseList':warehouseList,   'categoryList':categoryList,   'page_obj': page_obj})
        
    
  

@login_required
def outboundDeliveryView(request, requested_id):
   # pendingRequest = get_object_or_None(StockMovements, pk=requested_id)
    #print('pendingRequest product is:', pendingRequest.product)
    pendingTask = get_object_or_None(Tasks, pk=requested_id)
    if pendingTask:
        products = pendingTask.stockmovements_set.all()
    print('pendingTask is ', pendingTask)
    print('request is:', request.method)
    print('request product data', request.POST.get('producto_0'))
  
   # productsToReceive = pendingTask.stockmovements_set.all().values()
    #task = Tasks.objects.filter(task_id = requested_id)
    tasks = Tasks.objects.filter(task_id=requested_id, status='Pending').prefetch_related('stockmovements_set')

    numberOfProducts = request.POST.get('extra_field_count')
    print('number Of Products in OutboundDeliver view is', numberOfProducts)
     # if this is a POST request we need to process the form data
    if request.method == "POST":
        # create a form instance and populate it with data from the request:
        form = OutboundDeliveryForm(request.POST, instance= pendingTask, extra= request.POST.get('extra_field_count'))

        print('form is valid', form.is_valid())
      #  print('form is', form)
        print('form fields are', form.cleaned_data)

        # check whether it's valid:
        if form.is_valid():
            print('el form es valido')
           #product = form.cleaned_data['product']
           # date  =   form.cleaned_data['date']
            
           # print(product)
           # print(date)
            department = form.cleaned_data['department']
            issuer = form.cleaned_data['issuer']
            receptor = form.cleaned_data['receptor']
            warehouse = form.cleaned_data['warehouse']
            actionType = 'Confirma Egreso'
            motivoEgreso = form.cleaned_data['motivoEgreso']
            observations = form.cleaned_data['observations']
            deliveryDate = datetime.now().date()
            # StockMovements.objects.create(product = product, date=date, department=department,
            #                             issuer=issuer, actionType = actionType, cantidad=cantidad,
            #                             motivoEgreso=motivoIngreso,status='Pending')
            
            datalist = []
            # task = Tasks.objects.create(date= date, receptor= receptor, warehouse= warehouse, issuer= issuer,
            #                             motivoIngreso=motivoIngreso,  actionType=actionType, department=department)
            
            taskToUpdate = Tasks.objects.filter(task_id=requested_id)
            taskToUpdate.update(status='Confirmed', observations=observations, deliveryDate= deliveryDate)
            
            
            task = Tasks.objects.get(task_id=requested_id)
            
            for i , product in enumerate(products):
                form.fields['producto_{}'.format(i)] = product.product.name
                form.fields['cantidad_{}'.format(i)] = product.cantidad
                netQuantity = form.cleaned_data['cantidadNeta_{}'.format(i)]
                
                quantity = form.fields['cantidad_{}'.format(i)]
                diffQuantity = int(quantity) - int(netQuantity)
                newproduct = Product.objects.get(name= product.product.name, warehouse=warehouse)

                productToUpdate= Product.objects.filter(product_id= newproduct.product_id, warehouse=warehouse)
            
                print('productToUpdate is:', productToUpdate)

                productToUpdate.update(quantity = F('quantity') - netQuantity, deltaQuantity = F('deltaQuantity') + diffQuantity  )
            
                newProduct = StockMovements()

                newProduct.product = newproduct
                newProduct.actionType = actionType
                newProduct.cantidad = quantity
                newProduct.cantidadNeta = netQuantity
                newProduct.task = task

                # newProduct = StockMovements(product = newproduct, 
                #              actionType = actionType,
                #                          cantidad= quantity, cantidadNeta=netQuantity, task = task )
                
                datalist.append(newProduct)
            #print('new_product is:', datalist)
            print('form fields in view', form.fields)
            StockMovements.objects.bulk_create(datalist)     


            return redirect('/tasks/')
           
    else:

        form = OutboundDeliveryForm(instance= pendingTask ,
                                    initial={"task_id": requested_id })
        #form.task.queryset = Tasks.objects.filter(task_id = requested_id) 
        
    return render(request, "outboundDelivery.html", {"form": form, 'task_id': requested_id , "tasks": tasks})#, "numberOfProducts": len(productsToReceive)})

@login_required
def outboundConfirmedView(request, requested_id):
   # pendingRequest = get_object_or_None(StockMovements, pk=requested_id)
    #print('pendingRequest product is:', pendingRequest.product)
    # confirmedTask = get_object_or_None(Tasks, pk=requested_id)
    confirmedTask = Tasks.objects.filter(task_id=requested_id, status='Confirmed')
    print('confirmedTask is', confirmedTask)


    return render(request, 'outboundConfirmed.html', { 'task': confirmedTask[0]})

def finishTask(request, requested_id):


    print(requested_id)
    StockMovements.objects.filter(id=requested_id).update(status='Confirmed')
    #taskToConfirm.update(status='Confirmed')

    # taskToConfirm.save()
    
    return redirect('/tasks/')


class StockHistoryView(LoginRequiredMixin, generic.ListView):
    model = StockMovements

    template_name = 'stockhistory.html'

    def get_context_data(self, **kwargs):
        print('kwargs', self.kwargs)
        product_id = self.kwargs['product_id']
        product_name = Product.objects.filter(product_id=product_id)
        # Call the base implementation first to get the context
        context = super(StockHistoryView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        movements = StockMovements.objects.filter(product=product_id)
        context['movements'] = StockMovements.objects.filter(product=product_id)

        context['product'] = product_name[0].name
        return context 


def export_excel(request, dimension):

    print('requestGET')
    print('dimension is',dimension)
   
    

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="Inventario{}.xlsx"'.format(dimension)

    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = 'InventarioData{}'.format(dimension)

    if dimension == 'deposit':

        # Write header row
        header = ['Nombre', 'Codigo','Cantidad','Deposito','Categoria','Proveedor','Ubicacion','Stock de Seguridad']
        for col_num, column_title in enumerate(header, 1):
            cell = worksheet.cell(row=1, column=col_num)
            cell.value = column_title

        # Write data rows
        firstquery = Product.objects.all().select_related('warehouse')
        queryset = firstquery.values_list('name', 'internalCode','quantity','warehouse__name','category','supplier','location','stockSecurity')
 
        #list(Product.objects.all().values('name', 'internalCode','quantity','warehouse__name','category','supplier','location','stockSecurity'))

        for row_num, row in enumerate(queryset, 1):
            for col_num, cell_value in enumerate(row, 1):
                cell = worksheet.cell(row=row_num+1, column=col_num)
                cell.value = cell_value


    elif dimension == 'all':
         # Write header row
        header = ['Nombre', 'Codigo','CantidadTotal']
        for col_num, column_title in enumerate(header, 1):
            cell = worksheet.cell(row=1, column=col_num)
            cell.value = column_title

        # Write data rows
        #firstquery = Product.objects.all().select_related('warehouse')
        #queryset = firstquery.values_list('name', 'internalCode','quantity')
 
        queryset = Product.objects.values_list('name', 'internalCode').order_by('name').annotate(CantidadTotal=Sum('quantity'))
        #queryset = Product.objects.values('name','internalCode').order_by('name').annotate(=Sum('quantity'))
        #list(Product.objects.all().values('name', 'internalCode','quantity','warehouse__name','category','supplier','location','stockSecurity'))

        for row_num, row in enumerate(queryset, 1):
            for col_num, cell_value in enumerate(row, 1):
                cell = worksheet.cell(row=row_num+1, column=col_num)
                cell.value = cell_value

    workbook.save(response)

    
    return response

def handle_uploaded_file(file):

    file_data = pd.read_excel(file)

    return file_data

#     date = file_data['date'][0
#  = file_data['date'][0]
#     date = file_data['date'][0]
#     date = file_data['date'][0]
#     Cotization.objects.create(name=)
#     for i in range(0, len(file_data)):
#         producto = file_data.iloc[i]['product']
        
#         product_to_offer = Product.objects.get(name=producto)
        
        


def cotizationView(request,cotization_id):

    products = Product.objects.filter(hasOffer=cotization_id)#.values_list('name', 'quantityOffer','priceOffer')    
   # products = get_object_or_404(Product, hasOffer=cotization_id)
    print('products is', products)
    context = {'products':products}
    return render(request, 'modal.html', context)
    #return JsonResponse({'products': list(products)})


def newCotization(request):

    print('request.Files are')
    print(request.FILES)
    cotizations = Cotization.objects.all()
    if request.method == 'POST':
        form = CotizationForm(request.POST, request.FILES)
        if form.is_valid():
            print('el form es valido')
            data = handle_uploaded_file(request.FILES['file'])
            
            register_date = datetime.now().date()
            customer = form.cleaned_data['customer']
            observations = form.cleaned_data['observations']
            numberOfProducts = len(data)

            cotization = Cotization.objects.create(date=register_date, customer = customer, numberOfProducts=numberOfProducts,observations=observations)

            for i in range(0,len(data)):
                product_code = data.iloc[i]['codigo']
                product_quantity = data.iloc[i]['cantidad']
                product_price = data.iloc[i]['precio']
                productdb = Product.objects.filter(internalCode = product_code).update(hasOffer=cotization, quantityOffer=product_quantity,priceOffer=product_price)


            return HttpResponseRedirect('/success/url/')
    else:
        form = CotizationForm()
    
    return render(request, 'cotization.html', {'form': form, 'cotizations':cotizations})