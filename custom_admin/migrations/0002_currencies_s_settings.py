# Generated by Django 2.2.3 on 2019-09-19 18:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('custom_admin', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Settings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('activated', models.BooleanField(default=True)),
                ('service_fee', models.FloatField(default=0)),
                ('min_amount', models.FloatField(default=0)),
                ('max_amount', models.FloatField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Currencies_s',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('currency', models.CharField(max_length=50)),
                ('activated', models.BooleanField(default=True)),
                ('setting', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='custom_admin.Settings')),
            ],
        ),
    ]
