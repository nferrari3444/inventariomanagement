from django.urls import path, include
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from .views import index, inboundView, getProducts, getProduct, getProductsNames, outboundDeliveryView, outboundOrderView, finishTask, TaskListView, StockListView, StockHistoryView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('inbound/', inboundView, name='inbound'),
    path('outbound-order/', outboundOrderView, name='outboundorder'),
    path('outbound-delivery/<int:requested_id>', outboundDeliveryView, name='outbounddelivery'),
    path('finishtask/<int:requested_id>', finishTask,  name='finishtask'),
   
    path('tasks/', TaskListView.as_view() , name='tasks'),
    path('stock/', StockListView.as_view() , name='stock'),
    path('historical-movements/<int:product_id>', StockHistoryView.as_view(), name= "stockhistory" ) ,
    path('autocomplete-name', getProductsNames, name='autocomplete-name'),
    path('products/', getProducts, name='products'),
    path('product/<int:productId>/', getProduct, name='product')

]

urlpatterns += staticfiles_urlpatterns()