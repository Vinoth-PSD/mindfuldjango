# Generated by Django 5.1 on 2024-09-18 08:34

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Branches',
            fields=[
                ('branch_id', models.AutoField(primary_key=True, serialize=False)),
                ('branch_name', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'branches',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Locations',
            fields=[
                ('location_id', models.AutoField(primary_key=True, serialize=False)),
                ('address_line1', models.CharField(max_length=255)),
                ('address_line2', models.CharField(blank=True, max_length=255, null=True)),
                ('city', models.CharField(max_length=100)),
                ('state', models.CharField(max_length=100)),
                ('postal_code', models.CharField(max_length=20)),
                ('country', models.CharField(max_length=100)),
                ('latitude', models.DecimalField(decimal_places=6, max_digits=9)),
                ('longitude', models.DecimalField(decimal_places=6, max_digits=9)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'locations',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='ServiceProvider',
            fields=[
                ('provider_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('phone', models.CharField(max_length=20, unique=True)),
                ('password', models.CharField(max_length=255)),
                ('years_of_experience', models.IntegerField(blank=True, null=True)),
                ('skills', models.TextField(blank=True, null=True)),
                ('specializations', models.TextField(blank=True, null=True)),
                ('rating', models.DecimalField(blank=True, decimal_places=2, max_digits=3, null=True)),
                ('status', models.CharField(default='Active', max_length=20)),
                ('working_hours', models.TextField(blank=True, null=True)),
                ('available_slots', models.JSONField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('image_url', models.ImageField(blank=True, null=True, upload_to='provider_images/')),
            ],
            options={
                'db_table': 'serviceproviders',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='BeautyParlour',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('place', models.CharField(max_length=255)),
                ('star', models.IntegerField()),
                ('reviews', models.TextField()),
                ('image', models.ImageField(blank=True, null=True, upload_to='beauty_parlours/')),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('category_id', models.AutoField(primary_key=True, serialize=False)),
                ('category_name', models.CharField(max_length=100, unique=True)),
                ('status', models.CharField(default='Active', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='FAQHomeService',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(max_length=255)),
                ('answer', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='FAQSalonService',
            fields=[
                ('faqsalon_id', models.AutoField(primary_key=True, serialize=False)),
                ('question', models.CharField(max_length=255)),
                ('answer', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Login',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(max_length=15, unique=True)),
                ('otp', models.CharField(max_length=6)),
                ('otp_created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='ServiceTypes',
            fields=[
                ('service_type_id', models.AutoField(primary_key=True, serialize=False)),
                ('type_name', models.CharField(max_length=255)),
                ('status', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('user_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('phone', models.CharField(max_length=15, unique=True)),
                ('password', models.CharField(max_length=255)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_login', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('appointment_id', models.AutoField(primary_key=True, serialize=False)),
                ('appointment_date', models.DateField()),
                ('appointment_time', models.TimeField()),
                ('status', models.CharField(default='Pending', max_length=20)),
                ('otp', models.CharField(blank=True, max_length=10, null=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('provider', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='beautyapp.serviceprovider')),
            ],
        ),
        migrations.CreateModel(
            name='Beautician',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('role', models.CharField(max_length=100)),
                ('years_of_experience', models.CharField(max_length=100)),
                ('rating', models.FloatField()),
                ('profile_image', models.ImageField(upload_to='beauticians/')),
                ('provider', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='beautyapp.serviceprovider')),
            ],
        ),
        migrations.CreateModel(
            name='FAQ',
            fields=[
                ('faq_id', models.AutoField(primary_key=True, serialize=False)),
                ('question', models.CharField(max_length=255)),
                ('answer', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('provider', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='beautyapp.serviceprovider')),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('payment_id', models.AutoField(primary_key=True, serialize=False)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('payment_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('payment_status', models.CharField(default='Pending', max_length=20)),
                ('appointment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='beautyapp.appointment')),
            ],
        ),
        migrations.CreateModel(
            name='Services',
            fields=[
                ('service_id', models.AutoField(primary_key=True, serialize=False)),
                ('service_name', models.CharField(max_length=255)),
                ('price', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('status', models.CharField(default='Active', max_length=20)),
                ('image', models.ImageField(blank=True, null=True, upload_to='service_images/')),
                ('sku_value', models.CharField(max_length=255, null=True)),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='beautyapp.category')),
            ],
        ),
        migrations.CreateModel(
            name='Serviceprovidertype',
            fields=[
                ('provider_service_id', models.AutoField(primary_key=True, serialize=False)),
                ('price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('duration', models.IntegerField(blank=True, null=True)),
                ('status', models.CharField(default='Active', max_length=20)),
                ('provider_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='beautyapp.serviceprovider')),
                ('service_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='beautyapp.services')),
            ],
        ),
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('photo_id', models.AutoField(primary_key=True, serialize=False)),
                ('image', models.ImageField(upload_to='photos/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('provider', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='beautyapp.serviceprovider')),
                ('service_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='beautyapp.services')),
            ],
        ),
        migrations.AddField(
            model_name='appointment',
            name='service',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='beautyapp.services'),
        ),
        migrations.CreateModel(
            name='FilterProvider',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('rating', models.FloatField()),
                ('image', models.ImageField(blank=True, null=True, upload_to='provider_images/')),
                ('verified', models.BooleanField(default=False)),
                ('address', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='beautyapp.locations')),
                ('service_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='beautyapp.servicetypes')),
            ],
        ),
        migrations.CreateModel(
            name='Staff',
            fields=[
                ('staff', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('role', models.CharField(max_length=50)),
                ('years_of_experience', models.IntegerField(blank=True, null=True)),
                ('available_slots', models.JSONField(blank=True, null=True)),
                ('status', models.CharField(blank=True, null=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('provider', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='beautyapp.serviceprovider')),
            ],
        ),
        migrations.CreateModel(
            name='Subcategory',
            fields=[
                ('subcategory_id', models.AutoField(primary_key=True, serialize=False)),
                ('subcategory_name', models.CharField(max_length=100, unique=True)),
                ('status', models.CharField(default='Active', max_length=20)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subcategories', to='beautyapp.category')),
            ],
        ),
        migrations.AddField(
            model_name='services',
            name='subcategory',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='beautyapp.subcategory'),
        ),
        migrations.CreateModel(
            name='StaffReview',
            fields=[
                ('review_id', models.AutoField(primary_key=True, serialize=False)),
                ('rating', models.FloatField()),
                ('review', models.TextField(max_length=255)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('staff', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='beautyapp.staff')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='beautyapp.user')),
            ],
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('review_id', models.AutoField(primary_key=True, serialize=False)),
                ('rating', models.IntegerField()),
                ('comment', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('provider', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='beautyapp.serviceprovider')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='beautyapp.user')),
            ],
        ),
        migrations.CreateModel(
            name='CustomerFeedback',
            fields=[
                ('userfeedback_id', models.AutoField(primary_key=True, serialize=False)),
                ('feedback', models.TextField()),
                ('profile_image', models.ImageField(upload_to='profile_images/')),
                ('email', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='feedback_email', to='beautyapp.user')),
                ('user_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='feedback_by_user', to='beautyapp.user')),
            ],
        ),
        migrations.AddField(
            model_name='appointment',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='beautyapp.user'),
        ),
    ]
