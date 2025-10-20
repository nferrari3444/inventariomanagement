from .models import Product
from django.db.models import Avg, Count, Exists, OuterRef
from django.db.models import Count, F, Value, Q
import csv
from django.conf import settings
from io import StringIO 
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def check_stock_security():
    products = Product.objects.filter(quantity__lt = F('stockSecurity') * 1.1)

    # https://stackoverflow.com/questions/17584550/attach-generated-csv-file-to-email-and-send-with-django?rq=4
    csvfile = StringIO()
    csvwriter = csv.writer(csvfile)
    for product in products:
        csvwriter.writerow([product.name, product.internalCode, product.warehouse, product.quantity, product.stockSecurity])
    
    message = EmailMessage(
        "Productos A Reponer",
        "Productos Cerca de Stock de Seguridad",
        settings.EMAIL_HOST_USER,
        ["nferrari3444@gmail.com", "victoria.bonetti@filsa.com.uy"],
    )
    
    message.attach('productosAReponer.csv', csvfile.getvalue(), 'text/csv')

    message.send()
    


    