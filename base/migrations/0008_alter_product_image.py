# Generated by Django 5.0.2 on 2024-02-27 16:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0007_remove_order_description"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="image",
            field=models.FileField(blank=True, null=True, upload_to="products/"),
        ),
    ]
