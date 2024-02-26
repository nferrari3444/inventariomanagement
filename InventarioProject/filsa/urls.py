from django.urls import path, include
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from .views import index,  Login, Logout, Register, inboundView, getProducts, getProduct, getProductsNames, transferView, filterProducts, transferReceptionView, outboundDeliveryView, outboundOrderView, finishTask, inboundReceptionView, TaskListView, StockListView, StockHistoryView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('inbound/', inboundView, name='inbound'),
    path('inbound-reception/<int:requested_id>', inboundReceptionView, name='inboundreception'),
    path('outbound-order/', outboundOrderView, name='outboundorder'),
    path('outbound-delivery/<int:requested_id>', outboundDeliveryView, name='outbounddelivery'),
    path('transfer/', transferView, name='transfer'),
    path('transfer-reception/<int:requested_id>', transferReceptionView, name='transferreception'),
    path('finishtask/<int:requested_id>', finishTask,  name='finishtask'),
    path('tasks/', TaskListView.as_view() , name='tasks'),
    path('stock/', StockListView.as_view() , name='stock'),
    path('historical-movements/<int:product_id>', StockHistoryView.as_view(), name= "stockhistory" ) ,
    path('autocomplete-name', getProductsNames, name='autocomplete-name'),
    path('products/', getProducts, name='products'),
    path('product/<int:productId>/', getProduct, name='product'),
    path('products-filter/$', filterProducts, name='filterproducts'),
    path('accounts/login/', Login, name='login'),
    path('accounts/register/', Register, name='register'),
    path('accounts/logout/', Logout, name='logout')


]

urlpatterns += staticfiles_urlpatterns()