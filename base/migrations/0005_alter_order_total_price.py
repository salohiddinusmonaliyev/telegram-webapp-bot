# Generated by Django 5.0.2 on 2024-02-27 12:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0004_alter_order_time"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="total_price",
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]
