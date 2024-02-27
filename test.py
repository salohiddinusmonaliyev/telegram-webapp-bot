import requests
import json

json_data = requests.get("https://special-space-adventure-rq799wpxw442xgxr-8000.app.github.dev/api/order/")
json_data_order_item = requests.get("https://special-space-adventure-rq799wpxw442xgxr-8000.app.github.dev/api/order-item/")
items = json_data_order_item.json()
order = json_data.json()
order_list = []
for i in order:
    item_list = []
    for n in items:
        if n["order_id"] == i["id"]:
            item_list.append(n)
            i["items"] = item_list
            # print(order)

for i in order:
    if i["user"]=="+998905856779":
        print(i)