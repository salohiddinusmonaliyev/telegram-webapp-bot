from datetime import datetime

from django.shortcuts import render, redirect
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView

from base.models import CustomUser, Product
from base.serializer import *


# Create your views here.
class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class OrderViewSet(APIView):
    def get(self, request, pk=None):
        if pk==None:
            order = Order.objects.get(id=pk)
            ser = OrderSerializer(order)
            return Response(ser.data, status=status.HTTP_200_OK)


def home(request, s):
    data = {
        "products": Product.objects.all()
    }
    return render(request, 'index.html', data)


def order_add(request, s, user):
    orderitem = OrderItem.objects.filter(order__id=s, user=user)
    order_item = []
    for item in orderitem:
        order_item.append({item.id: item.quantity*(item.price-item.discount)})
    total_price = 0
    for order in orderitem:
        total_price = int((total_price + (order.price*order.quantity)))


    data = {
        "products": Product.objects.filter(),
        "order": s,
        "orderitem": orderitem,
        "total_price": total_price,
        "order_item": order_item,

    }
    return render(request, "index.html", data)


def order_create(request):
    saleid = Order.objects.create(time=datetime.now(), user=None)
    saleid = saleid.id
    return redirect(f'/add/{saleid}/')


def calculate_orderitem_total_price(price, quantity, discount):
    return (price-discount) * quantity

def orderitem_create(request, orderid, code, quantity):
    order = Order.objects.get(id=orderid, user=None)
    orderitems = OrderItem.objects.filter(user=None)
    product = Product.objects.get(code=code)

    existing_order_item = orderitems.filter(product=product, sell_id=order).first()

    if existing_order_item:
        existing_order_item.quantity += 1
        existing_order_item.total_price += (product.price)
        existing_order_item.save()
    else:
        total_price = calculate_orderitem_total_price(product.price, 1)
        OrderItem.objects.create(
            order_id=orderid,
            product=product,
            price=product.price,
            quantity=quantity,
            date=datetime.now(),
            total_price=total_price,
            user=None,
        )
    return redirect(f'/add/{orderid}/')