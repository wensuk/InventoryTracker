# Generated by Django 2.1.5 on 2020-05-04 22:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Attribute',
            new_name='Item',
        ),
    ]
