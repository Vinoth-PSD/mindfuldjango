# Generated by Django 5.1 on 2024-10-01 12:40

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('beautyapp', '0004_remove_photo_service_name_alter_review_rating_coupon'),
    ]

    operations = [
        migrations.CreateModel(
            name='ServiceFAQ',
            fields=[
                ('faq_id', models.AutoField(primary_key=True, serialize=False)),
                ('service_type', models.IntegerField()),
                ('question', models.TextField()),
                ('answer', models.TextField()),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.DeleteModel(
            name='FAQHomeService',
        ),
        migrations.DeleteModel(
            name='FAQSalonService',
        ),
    ]
