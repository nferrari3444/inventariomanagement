from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Avg, Count
from django.forms import inlineformset_factory
from django.db.models import Count, F, Value
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)
import json
from django.template.loader import render_to_string
from django.conf import settings
from datetime import datetime
from django.core import serializers
from django.views import generic
from annoying.functions import get_object_or_None
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse

from .forms import SignUpForm , InboundForm, OutboundOrderForm, OutboundDeliveryForm, InboundReceptionForm, TransferForm, TransferReceptionForm
from .models import CustomUser, StockMovements, DiffProducts, Product, Warehouses, Tasks
from django.core.cache import cache
from django.core.mail import send_mail
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

def index(request):
    return render(request, 'index.html')




def getProducts(request):
 
    if cache.get('all') is not None:
        objects = cache.get('all')

        print('data in cache', objects)
    else:
        objects = Product.objects.all()
        categories = Product.objects.all().values('category').distinct()
        suppliers = Product.objects.all().values('supplier').distinct()
        warehouses = Warehouses.objects.all().values('name').distinct()

        cache.set('products', objects)
        cache.set('categories', categories)
        cache.set('suppliers',suppliers) 
        cache.set('warehouses',warehouses)



    product = Product.objects.filter()
    product_data = Product.objects.values_list('name','product_id')
  #  data = serializers.serialize('json', product_data, fields=('name','barcode', 'internalCode'))

  #  print('product_data', product_data)
  #  print('data',data)
    
    list_data = list(product_data)
    json_data = dict(list_data)
    
    warehouses_list_data = list(warehouses)
   # warehouses_json_data = dict(warehouses_list_data)
    print(warehouses_list_data)
    suppliers_list_data = list(suppliers)
   # suppliers_json_data = dict(suppliers_list_data)

    categories_list_data = list(categories)
   # categories_json_data = dict(categories_list_data)


    print('json_data porducts is ', json_data)

    return JsonResponse({'products': json_data}) #, 'warehouses': warehouses_json_data,'categories':  categories_json_data, 'supplier': suppliers_json_data})


def getProductsNames(request):
    
    print('autocomplete', request.GET.get('term'))
    if 'term' in request.GET:
        qs = Product.objects.filter(name__istartswith=request.GET.get('term'))
        titles = []
        
        for product in qs:
            titles.append(product.name)
         
        print(titles)        
        return JsonResponse(titles, safe=False)


def getProduct(request, productId):

   

    product = Product.objects.filter(product_id=productId).values_list('barcode','internalCode','warehouse','location','category','supplier','quantity')

    product_data = Product.objects.values_list('name','barcode', 'internalCode')
    #data = serializers.serialize('json', product_data, fields=('name','barcode', 'internalCode'))

    print('product', product)
    #print('data',data)

    return JsonResponse({'product': list(product)})

def transferView(request):

    productNames = Product.objects.values_list('name', flat=True)
    print('extra_Field_count', request.POST.get('extra_field_count'))
    numberOfProducts = request.POST.get('extra_field_count')
    print('number of products in Inbound View is {}'.format(numberOfProducts))
    transferencia = StockMovements()
    # if this is a POST request we need to process the form data
    if request.method == "POST":
        # # create a form instance and populate it with data from the request:
        form = TransferForm(request.POST, request.FILES, extra = request.POST.get('extra_field_count'))
        # # check whether it's valid:
        print('form is valid', form.is_valid())
       
        if form.is_valid():
      
            date  =   datetime.today().strftime('%Y-%m-%d')
        
            receptor = form.cleaned_data['receptor']
            warehouse_out = form.cleaned_data['warehouse']
            solicitante = form.cleaned_data['issuer']
            department = form.cleaned_data['department']
            motivoIngreso = 'Transferencia'
            # motivoIngreso = form.cleaned_data['motivoIngreso']
            actionType = 'Transferencia'
       

            print('number of Products in form is {}'.format(numberOfProducts))
            datalist = []
            task = Tasks.objects.create(date= date, receptor= receptor, warehouse= warehouse_out, issuer=solicitante,
                                        motivoIngreso=motivoIngreso,  actionType=actionType, department=department)
            
            for i in range(0,int(numberOfProducts)):

                product = form.cleaned_data['product_{}'.format(i)]
                print('product in inbound view is {}'.format(product))
                productdb = Product.objects.get(name= product)
                
              
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
                inTransit = True

                
                productInTransit = Product.objects.create(name= product, warehouse= warehouse,
                                barcode= barcode, quantity = quantity, internalCode= internalCode, category= category,
                                location = location, supplier = supplier , deltaQuantity= deltaQuantity,
                                stockSecurity = stockSecurity, inTransit=inTransit)
                

                datalist.append(newProduct)

            print('new_product is:', datalist)

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
        
        form = TransferForm()

    return render(request, "transfer.html", {"form": form}) #, "products" :productNames})

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
            actionType = 'Recepcion Transferencia'
            # motivoIngreso = form.cleaned_data['motivoIngreso']
            
            # StockMovements.objects.create(product = product, date=date, department=department,
            #                             issuer=issuer, actionType = actionType, cantidad=cantidad,
            #                             motivoEgreso=motivoIngreso,status='Pending')
            
            datalist = []
            # task = Tasks.objects.create(date= date, receptor= receptor, warehouse= warehouse, issuer= issuer,
            #                             motivoIngreso=motivoIngreso,  actionType=actionType, department=department)
            
            taskToUpdate = Tasks.objects.filter(task_id=requested_id)
            taskToUpdate.update(status='Confirmed')
            
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
                    productToUpdate.update(quantity = F('quantity') + netQuantity, deltaQuantity = F('deltaQuantity') - diffQuantity  )
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
                    stockSecurity = productdb.stockSecurity
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
                    
                    # productInTransit = Product.objects.create(name= product, warehouse= warehouse,
                    #             barcode= barcode, quantity = quantity, internalCode= internalCode, category= category,
                    #             location = location, supplier = supplier , deltaQuantity= deltaQuantity,
                    #             stockSecurity = stockSecurity, inTransit=inTransit)
                
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

def inboundView(request):

    productNames = Product.objects.values_list('name', flat=True)
    print('extra_Field_count', request.POST.get('extra_field_count'))
    numberOfProducts = request.POST.get('extra_field_count')
    print('number of products in Inbound View is {}'.format(numberOfProducts))
    nuevoIngreso = StockMovements()
    # if this is a POST request we need to process the form data
    if request.method == "POST":
        # # create a form instance and populate it with data from the request:
        form = InboundForm(request.POST, request.FILES, extra = request.POST.get('extra_field_count'))
        # # check whether it's valid:
        print('form is valid', form.is_valid())
       # print('form is', form)
        # product = request.POST.get('product')
        # print('product in view is', product)
        # # print(form.cleaned_data['product'])
        if form.is_valid():
        #     # process the data in form.cleaned_data as 
        #     product = form.cleaned_data['product']
            date  =   datetime.today().strftime('%Y-%m-%d')
           # print('form is:', form)

        #     print(product)
        #     print(date)
            
            receptor = form.cleaned_data['receptor']
            warehouse = form.cleaned_data['warehouse']
            solicitante = form.cleaned_data['issuer']
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
                newproduct = Product.objects.get(name= product)
                
                # nuevoIngreso.barcode = form.cleaned_data['barcode_{}'.format(i)]
                # nuevoIngreso.internalCode = form.cleaned_data['internalCode_{}'.format(i)]
                quantity = form.cleaned_data['cantidad_{}'.format(i)]

                print('product is:', product)
                print('quantity is:', quantity)

                newProduct = StockMovements(product = newproduct, 
                             actionType = actionType,
                                         cantidad= quantity, task = task )
                
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
        #     print('cantidad in view is:', cantidad)

        #     StockMovements.objects.create(product = product, date=date, receptor=receptor,
        #                                 warehouse=warehouse, actionType = actionType,
        #                                 cantidad=cantidad, cantidadNeta=cantidadNeta,
        #                                 motivoIngreso=motivoIngreso)

        #     productToUpdate= Product.objects.filter(product_id=product.product_id, warehouse=warehouse)
            
        #     print('productToUpdate is:', productToUpdate)

        #     productToUpdate.update(quantity = F('quantity') + cantidadNeta)

        #     # Product.objects.update(name=product.name, warehouse=warehouse, quantity = F('quantity') + cantidadNeta,
        #     #                     deltaQuantity = F('deltaQuantity') + deltaDiff)
            
        #     productInWH = DiffProducts.objects.filter(warehouse=warehouse,product=product)

        #     if productInWH.exists():
        #         productInWH.update(totalPurchase= F('totalPurchase') + cantidad, 
        #                                 totalQuantity= F('totalQuantity') + cantidadNeta,
        #                                 productDiff=F('productDiff') + deltaDiff )
        #     else:
                
        #         DiffProducts.objects.create(product = product, warehouse=warehouse, totalPurchase=cantidad, 
        #                                 totalQuantity=cantidadNeta, productDiff= deltaDiff)

            # ...
            # redirect to a new URL:
            #return http.HttpResponseRedirect('')
            return redirect('/tasks/')
            #return HttpResponseRedirect("/inbound/")

    # if a GET (or any other method) we'll create a blank form
    else:
        
        form = InboundForm()

    return render(request, "inbound.html", {"form": form}) #, "products" :productNames})

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
            actionType = 'Recepcion Solicitud'
            motivoIngreso = form.cleaned_data['motivoIngreso']
            
            # StockMovements.objects.create(product = product, date=date, department=department,
            #                             issuer=issuer, actionType = actionType, cantidad=cantidad,
            #                             motivoEgreso=motivoIngreso,status='Pending')
            
            datalist = []
            # task = Tasks.objects.create(date= date, receptor= receptor, warehouse= warehouse, issuer= issuer,
            #                             motivoIngreso=motivoIngreso,  actionType=actionType, department=department)
            
            taskToUpdate = Tasks.objects.filter(task_id=requested_id)
            taskToUpdate.update(status='Confirmed')
            
            taskupdated = Tasks.objects.filter(task_id = requested_id).values_list('receptor', 'issuer','status', 'motivoIngreso','motivoEgreso','warehouse','actionType')
            print('taskupdated in view is ', taskupdated)
            task = Tasks.objects.get(task_id=requested_id)
            
            for i , product in enumerate(products):
                form.fields['producto_{}'.format(i)] = product.product.name
                form.fields['cantidad_{}'.format(i)] = product.cantidad
                netQuantity = form.cleaned_data['cantidadNeta_{}'.format(i)]
                
                quantity = form.fields['cantidad_{}'.format(i)]
                diffQuantity = int(quantity) - int(netQuantity)
                newproduct = Product.objects.get(name= product.product.name)

                productToUpdate= Product.objects.filter(product_id= newproduct.product_id, warehouse=warehouse)
            
                print('productToUpdate is:', productToUpdate)

                productToUpdate.update(quantity = F('quantity') + netQuantity, deltaQuantity = F('deltaQuantity') - diffQuantity  )
            

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

def outboundOrderView(request):
    print('request is:', request.method)
    print('request product data', request.POST.get('product'))
    product = request.POST.get('product')
    issuer = request.POST.get('issuer')
    
    numberOfProducts = request.POST.get('extra_field_count')

     # if this is a POST request we need to process the form data
    if request.method == "POST":
        
        form = OutboundOrderForm(request.POST, request.FILES, extra = request.POST.get('extra_field_count'))

        print('form is valid', form.is_valid())
        #print('form is', form)
        date  =   datetime.today().strftime('%Y-%m-%d')
           # print('form is:', form)

        #     print(product)
        #     print(date)
            
        receptor = form.cleaned_data['receptor']
        warehouse = form.cleaned_data['warehouse']
        solicitante = form.cleaned_data['issuer']
        department = form.cleaned_data['department']
        #     cantidad = form.cleaned_data['cantidad']
        #     cantidadNeta = form.cleaned_data['cantidadNeta']
        #     deltaDiff =  cantidadNeta - cantidad
        motivoEgreso = form.cleaned_data['motivoEgreso']
        actionType = 'Nuevo Egreso'
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
#            newProduct = StockMovements(product = newproduct, 
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
        form = OutboundOrderForm()

    return render(request, "outboundOrder.html", {"form": form})

class TaskListView(generic.ListView):
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
    

class StockListView(generic.ListView):
    model = Product

    template_name = 'stock.html'
    print('llega aca con el checkbox')
    # def get(self, request, *args, **kwargs):
    #     print('get request stocklistview')
    #    # stuff = self.get_queryset()
    #     warehouse = request.POST.get('warehouse',None)
    #     category = request.POST.get('category',None)
    #     supplier = request.POST.get('supplier',None)

    #     context = super(StockListView, self).get_context_data(**kwargs)

    #     context['productList'] = Product.objects.all().values('name').distinct()
    #     context['categoryList'] = Product.objects.all().values('category').distinct()
    #     context['supplierList'] = Product.objects.all().values('supplier').distinct()
    #     context['warehouseList'] = Warehouses.objects.all().values('name').distinct()


    #     if category:
    #         category_filter = True
    #         categoryList = [category]
    #     else:
    #         categoryList = Product.objects.all().values('category').distinct()

    #     if supplier:
    #         supplier_filter = True
    #         supplierList = [supplier]
        
    #     else:
    #         supplierList = Product.objects.all().values('supplier').distinct()

    #     if warehouse:
    #         warehouseList = list(Warehouses.objects.get(name=warehouse))
    #     else:
    #         warehouseList = Warehouses.objects.all()

    #     print('warehouse is', warehouse)
    #     print('category is', categoryList)
    #     print('supplier is', supplierList)
    #     #player__name__in
    #     filter_data = Product.objects.select_related('warehouse').filter(warehouse__name__in=[war for war in warehouseList], category__in =categoryList, supplier__in=supplierList) 
    #     # data = serializers.serialize("json", Product.objects.filter(warehouse=warehouse, category=category, supplier=supplier).select_related('warehouse') )
    #     print(filter_data)

    #     return    render(request, self.template_name, {'products': filter_data}) 

    # def post(self, request, *args, **kwargs):
    #     context = super().post(request, *args, **kwargs)
    #     foos = self.get_context_data().get('foos')
    #     # do stuff here
    #     return context
    
  
        #data = serializers.serialize('json', context)
        
    
        # context['products'] = filter_data
        #return context
       # render_to_response()
       # return render(request, 'stock.html', {'products': filter_data}) 

        #return HttpResponse(data, content_type="application/json")
   

    def get_context_data(self, *args, **kwargs):
        # Call the base implementation first to get the context
        products_obj = Product.objects.all().values()
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
            context.update({'products' : Product.objects.select_related('warehouse').filter(warehouse=warehouse, category ='Insumos')}) #, supplier ='De Salt') 
        else:
            warehouseList = Warehouses.objects.all()
            
            #context['products'] = Product.objects.select_related('warehouse').filter(category ='Insumos') #, supplier ='De Salt') 
        context['products'] = Product.objects.all().select_related('warehouse') #.filter(category__in=categoryList, supplier__in=supplierList) 
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
    
    # def get_queryset(self, **kwargs):
    #    qs = super().get_queryset(**kwargs)
    #    print('qs in get_query_set is', qs)
    #    return qs.filter(category='Insumos') #id=self.kwargs['pk'])
    #    return qs.filter(brand_id=self.kwargs['pk'])
    
    # def post(self, request, *args, **kwargs):
    #     print('post request view')

    #    # self.object_list = self.get_queryset() 

    #     warehouse = request.POST.get('warehouse',None)
    #     category = request.POST.get('category',None)
    #     supplier = request.POST.get('supplier',None)
        
    #    # context = super(StockListView, self).get_context_data(**kwargs)

    #     # context['productList'] = Product.objects.all().values('name').distinct()
    #     # context['categoryList'] = Product.objects.all().values('category').distinct()
    #     # context['supplierList'] = Product.objects.all().values('supplier').distinct()
    #     # context['warehouseList'] = Warehouses.objects.all().values('name').distinct()

    #     #context = super(StockListView, self).post(request, *args, **kwargs)
        
    #     if category:
    #         category_filter = True
    #         categoryList = [category]
    #     else:
    #         categoryList = Product.objects.all().values('category').distinct()

    #     if supplier:
    #         supplier_filter = True
    #         supplierList = [supplier]
        
    #     else:
    #         supplierList = Product.objects.all().values('supplier').distinct()

    #     if warehouse:
    #          warehouseList = Warehouses.objects.get(name=warehouse)
    #     # else:
    #     #     warehouseList = Warehouses.objects.all()
    #    # context = {}
    #     warehouse = Warehouses.objects.get(name='Anaya 2710')
    #     print('warehouse is', warehouse)
    #     print('category is', categoryList)
    #     print('supplier is', supplierList)
    #     #player__name__in
    #     #filter_data = Product.objects.select_related('warehouse').filter(warehouse=warehouse, category ='Insumos') #, supplier ='De Salt') 
    #     # data = serializers.serialize("json", Product.objects.filter(warehouse=warehouse, category=category, supplier=supplier).select_related('warehouse') )
    #     #print(filter_data)
    #     self.object_list = self.get_queryset()
        
    #     context = super(StockListView, self).get_context_data(**kwargs)
    #     #context = super().post(request, *args, **kwargs)
    #     self.get_queryset = self.get_context_data().get('products').filter(warehouse=warehouse, category ='Insumos')
    #    # context.update({'products': products})
    #     self.object_list = self.get_queryset
    #     print('context in post request is', self.object_list)

    #     context.update({'products': self.object_list})
    #     # do stuff here
    #     return render(request,'stock.html', context) 
    
  

def filterProducts(request):

    data = dict()
    print('llega acaaaaa')
    warehouse = request.GET.get('warehouse',None)
    category = request.GET.get('category',None)
    supplier = request.GET.get('supplier',None)
    
    product = request.GET.get('product',None)
    
    checkbox= request.GET.get('checkbox',None)

    if checkbox:
        products = Product.objects.select_related('warehouse')  
        data = dict() 
        product_dict  = {'products' : products}
        data['html_table'] =  render_to_string('inject_table.html',
                            context = product_dict,
                        request = request
                            )

        return JsonResponse(data)
    
    print('product is',product)
    if product:
        products = Product.objects.filter(name=product)
        context = {'products' : products}
        data['html_table'] =  render_to_string('inject_table.html',
                             context,
                             request = request
                             )
    
        return JsonResponse(data)

    # else:
    #     products = Product.objects.all()
    #     context = {'products' : products}
    #     data['html_table'] =  render_to_string('inject_table.html',
    #                          context,
    #                          request = request
    #                          )
    
    #     return JsonResponse(data)

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
        filter_data = Product.objects.select_related('warehouse').filter(warehouse=warehouse, category__in =categoryList, supplier__in=supplierList) 
    else:
        filter_data = Product.objects.select_related('warehouse').filter(category__in =categoryList, supplier__in=supplierList) 

   # data = serializers.serialize("json", Product.objects.filter(warehouse=warehouse, category=category, supplier=supplier).select_related('warehouse') )
    print(filter_data)

    context = {'products' : filter_data}
    context['productList'] = Product.objects.all().values('name').distinct()
    context['categoryList'] = Product.objects.all().values('category').distinct()
    context['supplierList'] = Product.objects.all().values('supplier').distinct()
    context['warehouseList'] = Warehouses.objects.all().values('name').distinct()
    
    data['html_table'] =  render_to_string('inject_table.html',
                             context,
                             request = request
                             )
    
    return JsonResponse(data)
    #data = serializers.serialize('json', filter_data)
    #return HttpResponse(data, content_type="application/json")

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
            
            # StockMovements.objects.create(product = product, date=date, department=department,
            #                             issuer=issuer, actionType = actionType, cantidad=cantidad,
            #                             motivoEgreso=motivoIngreso,status='Pending')
            
            datalist = []
            # task = Tasks.objects.create(date= date, receptor= receptor, warehouse= warehouse, issuer= issuer,
            #                             motivoIngreso=motivoIngreso,  actionType=actionType, department=department)
            
            taskToUpdate = Tasks.objects.filter(task_id=requested_id)
            taskToUpdate.update(status='Confirmed')
            
            
            task = Tasks.objects.get(task_id=requested_id)
            
            for i , product in enumerate(products):
                form.fields['producto_{}'.format(i)] = product.product.name
                form.fields['cantidad_{}'.format(i)] = product.cantidad
                netQuantity = form.cleaned_data['cantidadNeta_{}'.format(i)]
                
                quantity = form.fields['cantidad_{}'.format(i)]
                diffQuantity = int(quantity) - int(netQuantity)
                newproduct = Product.objects.get(name= product.product.name)
            
            # for i in range(0,int(numberOfProducts)):
            #     print('i is', i)
            #     product = form.cleaned_data['producto_{}'.format(i)]
            #     print('product is {}'.format(product))
                 
            #     newproduct = Product.objects.get(name= product)
            #     print('new products in view is {}'.format(newproduct))

            #     # nuevoIngreso.barcode = form.cleaned_data['barcode_{}'.format(i)]
            #     # nuevoIngreso.internalCode = form.cleaned_data['internalCode_{}'.format(i)]
            #     quantity = form.cleaned_data['cantidad_{}'.format(i)]
            #     netQuantity = form.cleaned_data['cantidadNeta_{}'.format(i)]

            #     diffQuantity = int(quantity) - int(netQuantity)
            #     print('product is:', product)
            #     print('quantity is:', quantity)

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
            
        # #print('request product data', request.POST.get('product'))
        # # create a form instance and populate it with data from the request:
        # form = OutboundDeliveryForm(request.POST, instance= pendingTask)

        # print('form is valid:' , form.is_valid)
        # # check whether it's valid:
        # if form.is_valid():
        #     product = form.cleaned_data['product']
        #     department = form.cleaned_data['department']
        #     issuer = form.cleaned_data['issuer']
        #     motivoEgreso = form.cleaned_data['motivoEgreso']
        #     cantidad = form.cleaned_data['cantidad']
        #     date = form.cleaned_data['date']
        #     receptor = form.cleaned_data['receptor']
        #     cantidadEntregada = form.cleaned_data['cantidadEntregada']
        #     deliveryDate = form.cleaned_data['deliveryDate']
        #     warehouse = form.cleaned_data['warehouse']
        #     actionType = 'Confirma Entrega'
        #     diffQuantity = cantidad - cantidadEntregada

        #     StockMovements.objects.create(product = product, date=date, receptor=receptor,
        #                                 warehouse=warehouse, actionType = actionType,
        #                                 cantidad=cantidad, cantidadEntregada=cantidadEntregada,
        #                                 motivoEgreso=motivoEgreso, status='Confirmed')

        #     productToUpdate= Product.objects.filter(product_id=product.product_id, warehouse=warehouse)
            
        #     print('productToUpdate is:', productToUpdate)

        #     productToUpdate.update(quantity = F('quantity') - cantidadEntregada, deltaQuantity = F('deltaQuantity') + diffQuantity  )
            
        #     # Antes estaba esta linea porque la tarea estaba para un producto y el StockMovement
        #     # también.    
        #     StockMovements.objects.filter(id=requested_id).update(status='Confirmed')
        
    
            return redirect('/tasks/') # requested_id=requested_id)
           
    else:

        form = OutboundDeliveryForm(instance= pendingTask ,
                                    initial={"task_id": requested_id })
        #form.task.queryset = Tasks.objects.filter(task_id = requested_id) 
        
    return render(request, "outboundDelivery.html", {"form": form, 'task_id': requested_id , "tasks": tasks})#, "numberOfProducts": len(productsToReceive)})

def finishTask(request, requested_id):


    print(requested_id)
    StockMovements.objects.filter(id=requested_id).update(status='Confirmed')
    #taskToConfirm.update(status='Confirmed')

    # taskToConfirm.save()
    
    return redirect('/tasks/')


class StockHistoryView(generic.ListView):
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
    