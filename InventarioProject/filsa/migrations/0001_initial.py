# Generated by Django 5.0.1 on 2024-04-11 23:43

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cotization',
            fields=[
                ('cotization_id', models.AutoField(primary_key=True, serialize=False)),
                ('date', models.DateField(blank=True, null=True, verbose_name='Fecha')),
                ('customer', models.CharField(blank=True, max_length=60, null=True)),
                ('numberOfProducts', models.IntegerField(blank=True, null=True)),
                ('observations', models.CharField(blank=True, max_length=500, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('username', models.CharField(max_length=40, verbose_name='Usuario')),
                ('password', models.CharField(max_length=100)),
                ('email', models.EmailField(default='', error_messages={'required': 'Please provide your email address.', 'unique': 'An account with this email exist'}, max_length=40, unique=True, verbose_name='Correo')),
                ('departamento', models.CharField(default='Sales', max_length=30, verbose_name='Departamento')),
                ('role', models.CharField(blank=True, max_length=40, null=True, verbose_name='Rol')),
                ('is_staff', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'Usuarios',
                'verbose_name_plural': 'Usuarios',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('product_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('barcode', models.CharField(max_length=100, verbose_name='Codigo de Barras')),
                ('internalCode', models.BigIntegerField(verbose_name='Codigo Interno')),
                ('quantity', models.FloatField()),
                ('category', models.CharField(default='Insumos', max_length=100)),
                ('supplier', models.CharField(default='', max_length=100)),
                ('stockSecurity', models.IntegerField(default=0)),
                ('quantityOffer', models.FloatField(blank=True, null=True)),
                ('priceOffer', models.FloatField(blank=True, null=True)),
                ('hasOffer', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, to='filsa.cotization')),
            ],
            options={
                'verbose_name': 'Stock Productos vs Seguridad',
                'verbose_name_plural': 'Stock Productos vs Seguridad',
            },
        ),
        migrations.CreateModel(
            name='WarehousesProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Deposito')),
                ('quantity', models.FloatField(default=0, verbose_name='Cantidad en Deposito')),
                ('location', models.CharField(blank=True, default='', max_length=100, null=True, verbose_name='Ubicacion')),
                ('deltaQuantity', models.FloatField()),
                ('inTransit', models.BooleanField(default=False)),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='filsa.product', verbose_name='Producto')),
            ],
            options={
                'verbose_name': 'Productos en Deposito',
                'verbose_name_plural': 'Productos en Deposito',
            },
        ),
        migrations.CreateModel(
            name='Tasks',
            fields=[
                ('task_id', models.AutoField(primary_key=True, serialize=False)),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Confirmed', 'Confirmed')], default='Pending', max_length=30)),
                ('department', models.CharField(choices=[('Ventas', 'Ventas'), ('Dirección', 'Dirección'), ('Administración', 'Administración'), ('Encargado Servicio Técnico', 'Encargado Servicio Técnico'), ('Servicio Técnico', 'Servicio Técnico'), ('Logística', 'Logística')], default='Sales', max_length=30)),
                ('date', models.DateField(verbose_name='Fecha')),
                ('deliveryDate', models.DateField(default='1970-01-01', verbose_name='Fecha')),
                ('motivoIngreso', models.CharField(choices=[('Devolución Mercadería', 'Devolución Mercadería'), ('Importación', 'Importación'), ('Compra en Plaza', 'Compra en Plaza'), ('Armado Nuevo Producto', 'Armado Nuevo Producto')], max_length=30)),
                ('motivoEgreso', models.CharField(choices=[('Servicio Técnico', 'Servicio Técnico'), ('Planta de Armado', 'Planta de Armado'), ('Ventas', 'Ventas'), ('Mantenimiento', 'Mantenimiento')], max_length=30)),
                ('actionType', models.CharField(default='Inbound', max_length=20)),
                ('observations', models.CharField(blank=True, max_length=500, null=True)),
                ('issuer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='issuer', to=settings.AUTH_USER_MODEL)),
                ('receptor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='receptor', to=settings.AUTH_USER_MODEL)),
                ('warehouseProduct', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='filsa.warehousesproduct')),
            ],
        ),
        migrations.CreateModel(
            name='StockMovements',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('actionType', models.CharField(default='Inbound', max_length=25)),
                ('cantidad', models.FloatField(default=0)),
                ('cantidadNeta', models.FloatField(default=0)),
                ('cantidadEntregada', models.FloatField(default=0)),
                ('image', models.ImageField(blank=True, null=True, upload_to='images/')),
                ('task', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='filsa.tasks')),
                ('warehouseProduct', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='filsa.warehousesproduct', verbose_name='Nombre de Producto')),
            ],
            options={
                'verbose_name': 'Detalle Movimiento Producto',
                'verbose_name_plural': 'Detalle Movimientos Productos',
            },
        ),
        migrations.CreateModel(
            name='DiffProducts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('totalPurchase', models.FloatField(verbose_name='Cantidad')),
                ('totalQuantity', models.FloatField(verbose_name='Cantidad Neta')),
                ('productDiff', models.IntegerField(verbose_name='Diferencia')),
                ('warehouseProduct', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='filsa.warehousesproduct')),
            ],
            options={
                'verbose_name': 'Faltante Producto Total',
                'verbose_name_plural': 'Faltante Productos Total',
            },
        ),
    ]
