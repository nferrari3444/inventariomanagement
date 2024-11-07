from django.urls import path, include
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from .views import (home,  Login, Logout, Register, filterProducts, getProductWarehouse,
                    StockListView,  newCotization, inboundView, getProducts, getProduct,
                    getProductsNames, transferView,  transferReceptionView,
                    transferConfirmedView, outboundDeliveryView, outboundOrderView,
                    outboundConfirmedView, finishTask, inboundReceptionView, inboundConfirmedView,
                    cotizationView, TaskListView,  StockHistoryView, cotizationDelete, editDeliveryTask,
                    export_excel, cancelTaskView, crudProducts, transferEditTask, inboundEditTask)

from django.contrib.auth.views import (
    LogoutView, 
    PasswordResetView, 
    PasswordResetDoneView, 
    PasswordResetConfirmView,
    PasswordResetCompleteView
)

from django.urls.base import reverse_lazy

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('inbound/', inboundView, name='inbound'),
    path('inbound-reception/<int:requested_id>', inboundReceptionView, name='inboundreception'),
    path('inbound-confirmed/<int:requested_id>', inboundConfirmedView, name='inboundconfirmed'),
    path('inbound-edit/<int:requested_id>', inboundEditTask, name='inboundedit'),
    path('outbound-order/', outboundOrderView, name='outboundorder'),
    path('outbound-delivery/<int:requested_id>', outboundDeliveryView, name='outbounddelivery'),

    path('outbound-confirmed/<int:requested_id>', outboundConfirmedView, name='outboundconfirmed'),
    path('transfer/', transferView, name='transfer'),
    path('transfer-reception/<int:requested_id>', transferReceptionView, name='transferreception'),
    path('transfer-edit/<int:requested_id>', transferEditTask, name='transferedit'),


    path('transfer-confirmed/<int:requested_id>', transferConfirmedView, name='transferconfirmed'),
  
    path('finishtask/<int:requested_id>', finishTask,  name='finishtask'),
    path('task-cancelled/<int:requested_id>', cancelTaskView, name='canceltask'),
    path('task-edited/<int:requested_id>', editDeliveryTask, name='editdeliverytask'),
    path('tasks/', TaskListView.as_view() , name='tasks'),
    path('new-cotization/', newCotization , name='newcotization'),
    path('products-crud/<str:action>', crudProducts, name='productscrud'),
    path('modal/<int:cotization_id>/', cotizationView , name='cotizationview'),
    path('delete-cotization/<int:cotization_id>/', cotizationDelete , name='deletecotization'),
    path('historical-movements/<int:product_id>', StockHistoryView.as_view(), name= "stockhistory" ) ,
    path('autocomplete-name', getProductsNames, name='autocomplete-name'),
    path('products/', getProducts, name='products'),

    path('product/<int:productId>/', getProduct, name='product'),
    path('product/$', getProductWarehouse, name='productwarehouse'),
    path('stock/', StockListView.as_view(), name='stock'),
    path('products-filter/$', filterProducts, name='filterproducts'),
    path('login/', Login, name='login'),
    path('accounts/login/', Login, name='login'),
    path('register/', Register, name='register'),
    path('logout/', Logout, name='logout'),
    path('password_reset/', PasswordResetView.as_view(template_name='registration/password_reset.html',
                                                       email_template_name='registration/password_reset_email.html'),name='password_reset'),
    path('password_reset/done/', PasswordResetDoneView.as_view(template_name='registration/password_reset_sent.html'),  name='password_reset_done'),
    path('reset_custom/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'),
                                                                    name='password_reset_confirm'),
    path('reset/done/',PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),name='password_reset_complete'),
    path('export_to_excel/<str:dimension>', export_excel, name='excel-export' )
]

# password-reset-confirm


urlpatterns += staticfiles_urlpatterns()