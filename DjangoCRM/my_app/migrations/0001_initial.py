# Generated by Django 4.1.5 on 2023-05-02 19:58

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('satisfaction_score', models.IntegerField()),
                #('customer_status', models.IntegerField()),
                ('cltv', models.IntegerField()),
                ('number_of_referrals', models.IntegerField()),
                ('tenure_in_months', models.IntegerField()),
                ('offer', models.CharField(max_length=255)),
                ('phone_service', models.BooleanField()),
                ('avg_monthly_long_distance_charges', models.FloatField()),
                ('multiple_lines', models.BooleanField()),
                ('internet_type', models.CharField(max_length=255)),
                ('avg_monthly_gb_download', models.IntegerField()),
                ('online_security', models.BooleanField()),
                ('online_backup', models.BooleanField()),
                #('device_protection_plan', models.BooleanField()),
                ('premium_tech_support', models.BooleanField()),
                ('streaming_tv', models.BooleanField()),
                ('streaming_movies', models.BooleanField()),
                ('streaming_music', models.BooleanField()),
                ('unlimited_data', models.BooleanField()),
                ('contract', models.CharField(max_length=255)),
                ('paperless_billing', models.BooleanField()),
                ('payment_method', models.CharField(max_length=255)),
                ('monthly_charge', models.FloatField()),
                ('total_charges', models.FloatField()),
                ('total_refunds', models.FloatField()),
                ('total_extra_data_charges', models.IntegerField()),
                ('total_long_distance_charges', models.FloatField()),
                ('population', models.IntegerField()),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('gender', models.CharField(max_length=255)),
                ('age', models.IntegerField()),
                ('married', models.BooleanField()),
                ('number_of_dependents', models.IntegerField()),
            ],
        ),
    ]
