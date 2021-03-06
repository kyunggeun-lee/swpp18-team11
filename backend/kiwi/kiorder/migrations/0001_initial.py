# Generated by Django 2.1.1 on 2018-09-29 08:28

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import sortedm2m.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0009_alter_user_last_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Franchise',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Purchasable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('base_price', models.DecimalField(decimal_places=10, max_digits=19)),
                ('franchise', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='kiorder.Franchise')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PurchasableCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('franchise', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='kiorder.Franchise')),
                ('purchasables', sortedm2m.fields.SortedManyToManyField(help_text=None, to='kiorder.Purchasable')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PurchasableOption',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('base_price', models.DecimalField(decimal_places=10, max_digits=19)),
                ('max_capacity', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Store',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('location', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('timezone', models.TextField()),
                ('next_number', models.IntegerField(default=0)),
                ('franchise', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='kiorder.Franchise')),
                ('purchasable_categories', sortedm2m.fields.SortedManyToManyField(help_text=None, to='kiorder.PurchasableCategory')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.CharField(choices=[('todo', 'Todo'), ('doing', 'Doing'), ('done', 'Done')], default='todo', max_length=16)),
                ('number', models.IntegerField()),
                ('removed', models.BooleanField(default=False)),
                ('denorm_data', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kiorder.Store')),
            ],
        ),
        migrations.CreateModel(
            name='Tx',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('utxid', models.CharField(max_length=255, unique=True)),
                ('reversed', models.BooleanField(default=False)),
                ('purchase_type', models.CharField(max_length=255, null=True)),
                ('purchase_data', models.TextField()),
                ('total_price', models.DecimalField(decimal_places=10, max_digits=19)),
                ('extra_props', models.TextField()),
                ('part_ref', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('store', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='kiorder.Store')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TxCredit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=10, max_digits=19)),
                ('reverse', models.BooleanField(default=False)),
                ('customer_name', models.CharField(max_length=255)),
                ('customer_ref', models.CharField(max_length=255)),
                ('customer_bank', models.CharField(max_length=255)),
                ('value_date', models.DateField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('tx', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kiorder.Tx')),
            ],
        ),
        migrations.CreateModel(
            name='TxItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('purchasable_name', models.CharField(max_length=255)),
                ('purchasable_base_price', models.DecimalField(decimal_places=10, max_digits=19)),
                ('qty', models.IntegerField()),
                ('price', models.DecimalField(decimal_places=10, max_digits=19)),
                ('total_price', models.DecimalField(decimal_places=10, max_digits=19)),
                ('purchasable', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='kiorder.Purchasable')),
                ('tx', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='kiorder.Tx')),
            ],
        ),
        migrations.CreateModel(
            name='TxItemOption',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('purchasable_option_name', models.CharField(max_length=255)),
                ('base_price', models.DecimalField(decimal_places=10, max_digits=19)),
                ('qty', models.IntegerField()),
                ('total_price', models.DecimalField(decimal_places=10, max_digits=19)),
                ('purchasable_option', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='kiorder.PurchasableOption')),
                ('tx_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kiorder.TxItem')),
            ],
        ),
        migrations.CreateModel(
            name='TxLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('utxid', models.CharField(max_length=255, unique=True)),
                ('reversed', models.BooleanField(default=False)),
                ('purchase_type', models.CharField(max_length=255, null=True)),
                ('purchase_data', models.TextField()),
                ('total_price', models.DecimalField(decimal_places=10, max_digits=19)),
                ('extra_props', models.TextField()),
                ('part_ref', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('state', models.CharField(choices=[('ready', 'Ready'), ('pending', 'Pending'), ('done', 'Done'), ('cancelled', 'Cancelled'), ('rollback', 'Rolled back')], default='ready', max_length=16)),
                ('store', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='kiorder.Store')),
                ('tx', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='kiorder.Tx')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='txitem',
            name='tx_log',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='kiorder.TxLog'),
        ),
        migrations.AddField(
            model_name='ticket',
            name='tx',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kiorder.Tx'),
        ),
        migrations.AddField(
            model_name='ticket',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='purchasable',
            name='purchasable_options',
            field=sortedm2m.fields.SortedManyToManyField(help_text=None, to='kiorder.PurchasableOption'),
        ),
        migrations.AddField(
            model_name='purchasable',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddIndex(
            model_name='tx',
            index=models.Index(fields=['user', 'created_at'], name='kiorder_tx_user_id_4d9149_idx'),
        ),
        migrations.AddIndex(
            model_name='tx',
            index=models.Index(fields=['user', 'store', 'created_at'], name='kiorder_tx_user_id_4b2e1c_idx'),
        ),
        migrations.AddIndex(
            model_name='ticket',
            index=models.Index(fields=['store', 'removed', 'created_at'], name='kiorder_tic_store_i_132ade_idx'),
        ),
    ]
