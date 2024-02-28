from django.urls import path, include
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from .views import index,  Login, Logout, Register,   inboundView, getProducts, getProduct, getProductsNames, transferView, filterProducts, transferReceptionView, outboundDeliveryView, outboundOrderView, finishTask, inboundReceptionView, TaskListView, StockListView, StockHistoryView, export_excel
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
    path('login/', Login, name='login'),
    path('accounts/login/', Login, name='login'),
    path('register/', Register, name='register'),
    path('logout/', Logout, name='logout'),
    path('password-reset/', PasswordResetView.as_view(template_name='registration/password_reset.html',
                                                      email_template_name='registration/password_reset_email.html'),name='password-reset'),
    path('password_reset/done/', PasswordResetDoneView.as_view(template_name='registration/password_reset_sent.html'),name='password_reset_done'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html',
                                                                     success_url=reverse_lazy('registration:password_reset_complete')),name='password_reset_confirm'),
    path('reset_password_complete',PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),name='password_reset_complete'),
    path('export_to_excel', export_excel, name='excel-export' )

]

# password-reset-confirm


urlpatterns += staticfiles_urlpatterns()