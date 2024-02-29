from django.db import models


# Create your models here.
class CustomUser(models.Model):
    first_name = models.CharField(max_length=250)
    last_name = models.CharField(max_length=250)
    username = models.CharField(max_length=250)
    telegram_id = models.CharField(max_length=250)

    def __str__(self):
        return self.username


class Product(models.Model):
    code = models.IntegerField()
    name = models.CharField(max_length=250)
    price = models.IntegerField()
    block_price = models.IntegerField(null=True)
    description = models.TextField()
    image = models.FileField(upload_to='products/', null=True, blank=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    time = models.DateField()
    total_price = models.CharField(max_length=250, null=True, blank=True)
    user = models.CharField(max_length=250, null=True, blank=True)


    def __str__(self):
        return f"{self.id}"


class OrderItem(models.Model):
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    price = models.IntegerField(null=True)
    quantity = models.CharField(max_length=250, null=True)

    def __str__(self):
        return self.product.name