# Generated by Django 4.2.1 on 2023-05-31 10:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0009_rename_name_category_category_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='listing',
            old_name='account',
            new_name='posted_by',
        ),
    ]
