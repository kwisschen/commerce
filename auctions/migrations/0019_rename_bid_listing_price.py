# Generated by Django 4.2.1 on 2023-06-03 10:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0018_rename_price_listing_bid'),
    ]

    operations = [
        migrations.RenameField(
            model_name='listing',
            old_name='bid',
            new_name='price',
        ),
    ]
