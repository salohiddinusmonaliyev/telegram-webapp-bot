from django.contrib import admin

from base.models import *

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)