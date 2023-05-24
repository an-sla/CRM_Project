# Generated by Django 4.1.5 on 2023-05-03 19:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('my_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerPersonalData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('customer_number', models.IntegerField(unique=True)),
            ],
        ),
        migrations.AlterModelOptions(
            name='customerdata',
            options={'verbose_name_plural': 'Customer Data'},
        ),
        migrations.AddField(
            model_name='customerdata',
            name='customer_personal_data',
            field=models.OneToOneField(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='my_app.customerpersonaldata'),
        ),
    ]
