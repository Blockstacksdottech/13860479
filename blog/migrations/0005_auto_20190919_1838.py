# Generated by Django 2.2.3 on 2019-09-19 18:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_auto_20190918_0306'),
    ]

    operations = [
        migrations.AlterField(
            model_name='posts',
            name='date',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
