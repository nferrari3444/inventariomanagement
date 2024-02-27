from django.urls import path, include
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from .views import index,  Login, Logout, Register,   inboundView, getProducts, getProduct, getProductsNames, transferView, filterProducts, transferReceptionView, outboundDeliveryView, outboundOrderView, finishTask, inboundReceptionView, TaskListView, StockListView, StockHistoryView
from django.contrib.auth.views import (
    LogoutView, 
    PasswordResetView, 
    PasswordResetDoneView, 
    PasswordResetConfirmView,
    PasswordResetCompleteView
)
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
    path('accounts/logout/', Logout, name='logout'),
    # path('password-reset/', ResetPasswordView.as_view(template_name='registration/password_reset_form.html'), name='password-reset'),
    # path('password-reset-confirm/<uidb64>/<token>/',
    #      PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'),
    #      name='password_reset_confirm'),

    # path('password-reset-complete/',
    #      PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),
    #      name='password_reset_complete')
     path('password-reset/', PasswordResetView.as_view(template_name='registration/password_reset.html',
                                                          html_email_template_name='registration/password_reset_email.html'),name='password-reset'),
    path('password_reset/done/', PasswordResetDoneView.as_view(template_name='registration/password_reset_sent.html'),name='password_reset_done'),
    path('accounts/password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'),name='password_reset_confirm'),
    path('accounts/password-reset-complete/',PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),name='password_reset_complete'),

]



urlpatterns += staticfiles_urlpatterns()