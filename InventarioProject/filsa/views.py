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
from datetime import datetime
from django.core import serializers
from django.views import generic
from annoying.functions import get_object_or_None
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse

from .forms import SignUpForm , InboundForm, OutboundOrderForm, OutboundDeliveryForm
from .models import CustomUser, StockMovements, DiffProducts, Product, Warehouses
from django.core.cache import cache

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
        
        cache.set('products', objects)

    product = Product.objects.filter()
    product_data = Product.objects.values_list('name','product_id')
  #  data = serializers.serialize('json', product_data, fields=('name','barcode', 'internalCode'))

  #  print('product_data', product_data)
  #  print('data',data)
    
    list_data = list(product_data)
    json_data = dict(list_data)
    print(json_data)

    return JsonResponse({'products': json_data})

def getProductsNames(request):
    
    if 'term' in request.GET:
        qs = Product.objects.filter(name__istartswith=request.GET.get('term'))
        titles = []
        
        for product in qs:
            titles.append(product.name)
         
        print(titles)        
        return JsonResponse(titles, safe=False)


def getProduct(request, productId):

   

    product = Product.objects.filter(product_id=productId).values_list('barcode','internalCode')

    product_data = Product.objects.values_list('name','barcode', 'internalCode')
    #data = serializers.serialize('json', product_data, fields=('name','barcode', 'internalCode'))

    print('product', product)
    #print('data',data)

    return JsonResponse({'product': list(product)})

def inboundView(request):

    productNames = Product.objects.values_list('name', flat=True)
    # if this is a POST request we need to process the form data
    if request.method == "POST":
        # create a form instance and populate it with data from the request:
        form = InboundForm(request.POST, request.FILES)
        # check whether it's valid:
        print('form is valid', form.is_valid())

        product = request.POST.get('product')
        print('product in view is', product)
        # print(form.cleaned_data['product'])
        if form.is_valid():
            # process the data in form.cleaned_data as 
            product = form.cleaned_data['product']
            date  =   datetime.today().strftime('%Y-%m-%d')
            
            print(product)
            print(date)
            receptor = form.cleaned_data['receptor']
            warehouse = form.cleaned_data['warehouse']
            cantidad = form.cleaned_data['cantidad']
            cantidadNeta = form.cleaned_data['cantidadNeta']
            deltaDiff =  cantidadNeta - cantidad
            motivoIngreso = form.cleaned_data['motivoIngreso']
            actionType = 'Nuevo Ingreso'

            print('cantidad in view is:', cantidad)

            StockMovements.objects.create(product = product, date=date, receptor=receptor,
                                        warehouse=warehouse, actionType = actionType,
                                        cantidad=cantidad, cantidadNeta=cantidadNeta,
                                        motivoIngreso=motivoIngreso)

            productToUpdate= Product.objects.filter(product_id=product.product_id, warehouse=warehouse)
            
            print('productToUpdate is:', productToUpdate)

            productToUpdate.update(quantity = F('quantity') + cantidadNeta)

            # Product.objects.update(name=product.name, warehouse=warehouse, quantity = F('quantity') + cantidadNeta,
            #                     deltaQuantity = F('deltaQuantity') + deltaDiff)
            
            productInWH = DiffProducts.objects.filter(warehouse=warehouse,product=product)

            if productInWH.exists():
                productInWH.update(totalPurchase= F('totalPurchase') + cantidad, 
                                        totalQuantity= F('totalQuantity') + cantidadNeta,
                                        productDiff=F('productDiff') + deltaDiff )
            else:
                
                DiffProducts.objects.create(product = product, warehouse=warehouse, totalPurchase=cantidad, 
                                        totalQuantity=cantidadNeta, productDiff= deltaDiff)

            # ...
            # redirect to a new URL:
            #return HttpResponseRedirect("/thanks/")

    # if a GET (or any other method) we'll create a blank form
    else:
        form = InboundForm()

    return render(request, "inbound.html", {"form": form, "products" :productNames})


def outboundOrderView(request):
    print('request is:', request.method)
    print('request product data', request.POST.get('product'))
    product = request.POST.get('product')
    issuer = request.POST.get('issuer')
    
    
     # if this is a POST request we need to process the form data
    if request.method == "POST":
        
        form = OutboundOrderForm(request.POST)

        print('form is valid', form.is_valid())
        #print('form is', form)

        # check whether it's valid:
        if form.is_valid():
            print('el form es valido')
            product = form.cleaned_data['product']
            date  =   form.cleaned_data['date']
            
            print(product)
            print(date)
            department = form.cleaned_data['department']
            issuer = form.cleaned_data['issuer']
            cantidad = form.cleaned_data['cantidad']
            actionType = 'Nueva Solicitud'
            motivoEgreso = form.cleaned_data['motivoEgreso']
            
            StockMovements.objects.create(product = product, date=date, department=department,
                                        issuer=issuer, actionType = actionType, cantidad=cantidad,
                                        motivoEgreso=motivoEgreso,status='Pending')
            
    else:
        form = OutboundOrderForm()

    return render(request, "outboundOrder.html", {"form": form})

class TaskListView(generic.ListView):
    template_name = 'tasks.html'
    model = StockMovements

    
    

    def get_queryset(self) -> QuerySet[Any]:
        self.tasks = StockMovements.objects.filter(status='Pending' , actionType='Nueva Solicitud')

        return self.tasks
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(TaskListView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        context['tasks'] = self.tasks
        return context 
    
    


    #return render( "tasks.html")

class StockListView(generic.ListView):
    model = Product

    template_name = 'stock.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        products_obj = Product.objects.all().values()
        context = super(StockListView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        context['products'] = Product.objects.all().select_related('warehouse') 
        
        #Product.objects.all().values('name','barcode','internalCode','location',
        #                                            'warehouse', 'category', 'supplier', 'quantity')

        context['productList'] = Product.objects.all().values('name').distinct()
        context['categoryList'] = Product.objects.all().values('category').distinct()
        context['supplierList'] = Product.objects.all().values('supplier').distinct()
        context['warehouseList'] = Warehouses.objects.all().values('name').distinct()

        return context
    
def outboundDeliveryView(request, requested_id):
    pendingRequest = get_object_or_None(StockMovements, pk=requested_id)
    print('pendingRequest product is:', pendingRequest.product)


    print('requested_id is:', requested_id)
     # if this is a POST request we need to process the form data
    if request.method == "POST":
        #print('request product data', request.POST.get('product'))
        # create a form instance and populate it with data from the request:
        form = OutboundDeliveryForm(request.POST, instance= pendingRequest)

        print('form is valid:' , form.is_valid)
        # check whether it's valid:
        if form.is_valid():
            product = form.cleaned_data['product']
            department = form.cleaned_data['department']
            issuer = form.cleaned_data['issuer']
            motivoEgreso = form.cleaned_data['motivoEgreso']
            cantidad = form.cleaned_data['cantidad']
            date = form.cleaned_data['date']
            receptor = form.cleaned_data['receptor']
            cantidadEntregada = form.cleaned_data['cantidadEntregada']
            deliveryDate = form.cleaned_data['deliveryDate']
            warehouse = form.cleaned_data['warehouse']
            actionType = 'Confirma Entrega'
            diffQuantity = cantidad - cantidadEntregada

            StockMovements.objects.create(product = product, date=date, receptor=receptor,
                                        warehouse=warehouse, actionType = actionType,
                                        cantidad=cantidad, cantidadEntregada=cantidadEntregada,
                                        motivoEgreso=motivoEgreso, status='Confirmed')

            productToUpdate= Product.objects.filter(product_id=product.product_id, warehouse=warehouse)
            
            print('productToUpdate is:', productToUpdate)

            productToUpdate.update(quantity = F('quantity') - cantidadEntregada, deltaQuantity = F('deltaQuantity') + diffQuantity  )
            

            StockMovements.objects.filter(id=requested_id).update(status='Confirmed')
            #taskToConfirm = StockMovements.objects.filter(id=requested_id)
            #print('taskToConfirm is:', taskToConfirm)
            #taskToConfirm.update(status='Confirmed')

            # taskToConfirm.save()
    
            return redirect('/tasks/') # requested_id=requested_id)
           
#return redirect('finishtask', requested_id)
            # ['product','department','issuer', 'motivoEgreso', 'cantidad', 'date',
            #       'receptor', 'cantidadEntregada', 'deliveryDate']
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
#return HttpResponseRedirect("tasks/")

    # if a GET (or any other method) we'll create a blank form
    else:
        form = OutboundDeliveryForm(instance= pendingRequest)
        

    return render(request, "outboundDelivery.html", {"form": form , 'task_id': requested_id })


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
        # Call the base implementation first to get the context
        context = super(StockHistoryView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        context['movements'] = StockMovements.objects.filter(product=product_id)
        return context 
    