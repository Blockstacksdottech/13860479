# Generated by Django 2.2.3 on 2019-09-16 18:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exchanger_app', '0004_auto_20190901_1206'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pending',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('currency', models.CharField(max_length=255)),
                ('amount', models.FloatField(default=0)),
            ],
        ),
    ]