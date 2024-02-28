from datetime import datetime, timedelta
import json
import requests


json_data = requests.get("https://zedproject.pythonanywhere.com/api/order/")
json_data_order_item = requests.get("https://zedproject.pythonanywhere.com/api/order-item/")
items = json_data_order_item.json()
data = json_data.json()


# Function to parse date string to datetime object
def parse_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d")

# Calculate the first day of the previous month
today = datetime.today()
first_day_of_current_month = today.replace(day=1)
last_day_of_previous_month = first_day_of_current_month - timedelta(days=1)
first_day_of_previous_month = last_day_of_previous_month.replace(day=1)

# Filter items for the last month
last_month_items = [item for item in data if parse_date(item['time']) >= first_day_of_previous_month and parse_date(item['time']) <= last_day_of_previous_month]

# Print the last month items
data = json.dumps(last_month_items, indent=4)
print(data)