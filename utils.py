import re
import pandas as pd
from geopy.geocoders import Nominatim
from datetime import datetime

from environs import Env

import json
import requests
import xlsxwriter

env = Env()
env.read_env()

pattern = r'\+998\d{9}\b'
ADMINS = env.list("ADMINS")

def validate_phone_number(phone_number):
	if re.match(pattern, phone_number):
		return True
	else:
		return False

def save_data_to_excel(phone_number, items_data, text):
    file_name = phone_number
    excel_filename = f'history/{file_name}.xlsx'

    # Create a new Excel workbook
    workbook = xlsxwriter.Workbook(excel_filename)
    worksheet = workbook.add_worksheet()

    # Write column headers
    headers = ['Buyurtma raqami', 'Mahsulot', 'Narxi', 'Miqdori', 'Sana']
    for col_num, header in enumerate(headers):
        worksheet.write(0, col_num, header)

    # Write data to Excel
    row = 1
    for item in items_data:
        worksheet.write(row, 0, item.get('Buyurtma raqami', ''))
        worksheet.write(row, 1, item.get('Mahsulot', ''))
        worksheet.write(row, 2, item.get('Narxi', ''))
        worksheet.write(row, 3, item.get('Miqdori', ''))
        worksheet.write(row, 4, item.get('Sana', ''))
        row += 1

    # Close the workbook
    workbook.close()

    return file_name


def get_location_name(latitude, longitude):
    geolocator = Nominatim(user_agent="location_finder")
    location = geolocator.reverse((latitude, longitude), language='en')
    return location.address

def parse_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d")

def is_admin(user_id):
	if str(user_id) in ADMINS:
		return True
	else:
		return False

def extract_numbers(data):
    pattern = re.compile(r'done-(\d+)')
    match = pattern.search(data)
    if match:
        number = int(match.group(1))
        print(number)
        return number