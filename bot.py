import json
import logging
import re
import requests
from datetime import date, datetime, timedelta
# from dateutil.relativedelta import relativedelta
import pandas as pd
import calendar
import time

from telegram import KeyboardButton, ReplyKeyboardMarkup, Update, WebAppInfo, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler


from geopy.geocoders import Nominatim

def get_location_name(latitude, longitude):
    geolocator = Nominatim(user_agent="location_finder")
    location = geolocator.reverse((latitude, longitude), language='en')
    return location.address


pattern = r'\+998\d{9}\b'


ADMIN = "6513420947"
# logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
# logger = logging.getLogger(__name__)

START, LOCATION, ORDER, CONTACT, PHONE_NUMBER, HISTORY, CHECK = range(7)


async def start(update: Update, context):
    user_id = str(update.effective_user.id)
    buttons = [["🛍 Buyurtma berish", "ℹ️ Biz haqimizda"]]
    admin_buttons = [["📄 Buyurtmalar tarixini olish"], ["🛍 Buyurtma berish", "ℹ️ Biz haqimizda"]]
    if user_id == ADMIN:
        await update.message.reply_text(f"Salom", reply_markup=ReplyKeyboardMarkup(admin_buttons, resize_keyboard=True))
    else:
        await update.message.reply_text("Salom", reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True))
    return START


async def menu(update: Update, context):
    await update.message.reply_text("Menyu\n/start ni bosing")

async def contact_us(update: Update, context):
    await update.message.reply_text("Contact\n/start ni bosing")


async def begin(update: Update, context):
    text = update.message.text
    if text == "🛍 Buyurtma berish":
        await update.message.reply_text("Buyurtma berish uchun birinchi navbatda joylashuvingizni yuboring",
                                        reply_markup=ReplyKeyboardMarkup.from_button(
                                            KeyboardButton(text="📍Joylashuvni yuborish", request_location=True),
                                            resize_keyboard=True,
                                        ))
        return LOCATION
    elif text == "ℹ️ Biz haqimizda":
        await update.message.reply_text("Buyurtma berish uchun /start ni bosing", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    elif text == "📄 Buyurtmalar tarixini olish":
        await update.message.reply_text("Iltimos, mijoz telefon raqamini (+998CCXXXXXXX) kiriting:", reply_markup=ReplyKeyboardRemove())
        return PHONE_NUMBER
    elif text == "/start":
        return await start(update, context)
    elif text == "/menu":
        return await menu(update, context)
    elif text == "/contact_us":
        return await contact_us(update, context)
    else:
        await update.message.reply_text("🚫🚫🚫")
        return await start(update, context)
        return ConversationHandler.END


async def phone_number(update: Update, context):
    # print(update.message.text)
    if re.match(pattern, update.message.text):
        user_data = context.user_data
        user_data["phone_number"] = update.message.text
        await update.message.reply_text("Muddatni tanlang:", reply_markup=ReplyKeyboardMarkup(
            [["📆 O'tgan oy", "🗓 O'tgan yil"]], resize_keyboard=True))
        return HISTORY
    else:
        await update.message.reply_html("❌ Iltimos, raqamni <b>+998CCXXXXXXX</b> formatida kiriting.")
        return PHONE_NUMBER


async def history(update: Update, context):
    # print(update.message.text)
    if update.message.text == "📆 O'tgan oy" or update.message.text == "🗓 O'tgan yil":   
        message = await update.message.reply_text("Iltimos, biroz kuting")

        phone_number = context.user_data['phone_number']
        json_data = requests.get("https://zedproject.pythonanywhere.com/api/order/")
        json_data_order_item = requests.get("https://zedproject.pythonanywhere.com/api/order-item/")
        items = json_data_order_item.json()
        orders = json_data.json()
        order_list = []
        for order in orders:
            item_list = [item for item in items if item["order_id"] == order["id"] and order["user"] == phone_number]
            if item_list:
                order["items"] = item_list
                order_list.append(order)

        def parse_date(date_str):
            return datetime.strptime(date_str, "%Y-%m-%d")

        today = datetime.today()
        # today = today.date()
        # print(today.date())
        if update.message.text == "📆 O'tgan oy":
            first_day_of_current_month = today.replace(day=1)
            last_day_of_previous_month = first_day_of_current_month - timedelta(days=1)
            first_day_of_previous_month = last_day_of_previous_month.replace(day=1)
            time1, time2 = first_day_of_previous_month.date(), last_day_of_previous_month.date()
            items = [item for item in order_list if parse_date(item['time']) >= first_day_of_previous_month and
                    parse_date(item['time']) <= last_day_of_previous_month]
        elif update.message.text == "🗓 O'tgan yil":
            start_last_year = datetime(today.year - 1, 1, 1)
            end_last_year = start_last_year.replace(year=today.year - 1, month=12, day=31)
            start_last_year_str, end_last_year_str = start_last_year.strftime('%Y-%m-%d'), end_last_year.strftime('%Y-%m-%d')
            time1, time2 = start_last_year_str, end_last_year_str
            items = [item for item in order_list if item["time"] >= start_last_year_str and item["time"] <= end_last_year_str]

        items_data = []
        for order in items:
            order_date = order["time"]
            for item in order['items']:
                product_response = requests.get("https://zedproject.pythonanywhere.com/api/product/")
                product_json = product_response.json()
                product = next((p["name"] for p in product_json if p["id"] == item["product"]), None)

                item['Buyurtma raqami'] = item.pop("order_id")
                del item["id"]
                item["Mahsulot"] = product
                del item["product"]
                item["Narxi"] = item.pop("price")
                item["Miqdori"] = item.pop("quantity")
                item["Sana"] = order_date
                items_data.append(item)

        df = pd.DataFrame(items_data)
        file_name = f"{phone_number} - {update.message.text}"
        excel_filename = f'history/{file_name}.xlsx'
        df.to_excel(excel_filename, index=False)
        await context.bot.deleteMessage(chat_id=update.message.chat_id,
                                    message_id=message.id)
        await update.message.reply_document(document=f"history/{file_name}.xlsx",
                                            caption=f"<b>📄 Buyurtmalar tarixi</b>\n\n👤 Foydalanuvchi: {phone_number}\n<b>🗓 {time1} - {time2}</b>",
                                            parse_mode="HTML", reply_markup=ReplyKeyboardRemove())
        await update.message.reply_text("Botni qayta ishga tushirish uchun /start ni bosing.")
        return ConversationHandler.END
    else:
        await update.message.reply_text("Xatolik")
        await update.message.reply_text("/start ni bosib botni qayta ishga tushiring")
        return ConversationHandler.END

async def get_location(update: Update, context):
    global user_location
    if update.message.location:
        user_location = update.message.location
    else:
        user_location = update.message.text
    await update.message.reply_text(
        "Buyurtma berish uchun pastdagi tugmani bosing.",
        reply_markup=ReplyKeyboardMarkup.from_button(
            KeyboardButton(
                text="🛒 Buyurtmma berish",
                web_app=WebAppInfo(url="https://zedproject.pythonanywhere.com/"),
            ), resize_keyboard=True, input_field_placeholder="Buyurtma bering"
        ),
    )
    return ORDER


async def web_app_data(update: Update, context):
    global data
    data = json.loads(update.effective_message.web_app_data.data)
    text = ""
    total_price = 0
    # print(data)
    for i in data:
        if i["quantity"] != 0 and i['quantity'] is not None:
            totalprice = int(i["quantity"]) * float(i["price"])
            total_price += totalprice
            totalprice = "{:,.0f}".format(totalprice).replace(",", " ")
            piece_or_block = None
            if i["selectedOption"][:4] == "dona":
                piece_or_block = "dona"
            elif i["selectedOption"][:4] == "blok":
                piece_or_block = "blok"
            text = (f"{text}\n\n👉 Mahsulot nomi: {i['title']}\nMiqdori: {i['quantity']} <b>{piece_or_block}</b>"
                    f"\nBir dona mahsulot narxi: {i['price']} so'm\nUmumiy narx: {totalprice} so'm")

    total_price = "{:,.0f}".format(total_price).replace(",", " ")

    await update.message.reply_text(f"{text}\n\n<b>💰 Umumiy narx: {total_price} so'm</b>", parse_mode="HTML")
    yes_no = [["✅ Ha", "❌ Yo'q"]]
    await update.message.reply_text(
        "✅ Buyurtmalar qabul qilindi\n\n<b>Buyurtmani tasdiqlaysizmi?</b>",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardMarkup(
            yes_no,
            resize_keyboard=True
        )
    )
    global order_items
    global order_total_price
    order_total_price = total_price
    order_items = text
    return CHECK

async def check(update: Update, context):
    if update.message.text == "✅ Ha":
        await update.message.reply_html("✅ Buyurtma tasdiqlandi")
        await update.message.reply_text(
            "✅ Buyurtmalar qabul qilindi\n\nTelefon raqamingizni yuboring. \n(<b>☎️ Telefon raqamni yuborish</b> tugmasini bosing Yoki raqamingizni quyidagi formatda kiriting (<b>+998CCXXXXXXX</b>)",
            parse_mode="HTML",
            reply_markup=ReplyKeyboardMarkup.from_button(
                KeyboardButton(text="☎️ Telefon raqamni yuborish", request_contact=True),
                resize_keyboard=True
            )
        )
        return CONTACT
    elif update.message.text == "❌ Yo'q":
        await update.message.reply_html("❌ Buyurtma rad etildi.")
        await update.message.reply_text("Botni qayta ishga tushirish uchun /start ni bosing", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

async def get_contact(update: Update, context):
    global contact
    
    if update.message.contact:
        contact = update.message.contact.phone_number
    else:
        contact = update.message.text
        if re.match(pattern, contact):
            await update.message.reply_text("✅ Telefon raqam qabul qilindi", reply_markup=ReplyKeyboardRemove())
            contact = update.message.text
        else:
            await update.message.reply_text("❌ Iltimos, raqamingizni quyidagi formatda kiriting (<b>+998CCXXXXXXX</b>)",
                                            parse_mode="HTML")
            return CONTACT



    message = await update.message.reply_text("Iltimos, biroz kuting ⏳")


    # print(user_location)
    try:
        location = await context.bot.send_location(chat_id=ADMIN, latitude=user_location.latitude, longitude=user_location.longitude)
        g_map = f"https://www.google.com/maps/@{user_location.latitude},{user_location.longitude},315m/data=!3m1!1e3?hl=en-US&entry=ttu"
        user_location_msg = f"<a href='{g_map}'>{get_location_name(latitude=user_location.latitude, longitude=user_location.longitude)}</a>"
    except AttributeError:
        user_location_msg = user_location
    user_data = f"{order_items}\n\n<b>☎️ Telefon raqam: {contact}</b>\n<b>📍 Manzil: {user_location_msg}</b>"


    json_data = {
        "time": f"{date.today()}",
        "description": "none",
        "total_price": order_total_price,
        "user": f"{contact}"
    }

    order_response = requests.post(url="https://zedproject.pythonanywhere.com/api/order/", json=json_data)
    
    for i in data:
        if i["quantity"] != 0 and i['quantity'] is not None:
            piece_or_block = None
            if i["selectedOption"][:4] == "dona":
                piece_or_block = "dona"
            elif i["selectedOption"][:4] == "blok":
                piece_or_block = "blok"
            order_item_data = {
                "order_id": order_response.json()["id"],
                "price": i["price"],
                "quantity": f"{i["quantity"]} {piece_or_block}",
                "product": i["id"],
            }
            order_item_response = requests.post(url="https://zedproject.pythonanywhere.com/api/order-item/",
                                                json=order_item_data)
    await context.bot.deleteMessage(chat_id=update.message.chat_id, message_id=message.id)
    await update.message.reply_text("Buyurtma qabul qilindi. Tez orada siz bilan bo'glanishadi.",
                                    reply_markup=ReplyKeyboardRemove())

    await update.message.reply_text("Yangi buyurtma berish uchun <b>/start</b> ni bosing", reply_markup=ReplyKeyboardRemove(),
                                    parse_mode="HTML")


    await context.bot.send_message(chat_id=ADMIN,
                                   text=(
                                       f"<b>🆕 Yangi buyurtma</b>{user_data}\n\n<b>💰 Umumiy narx: {order_total_price} so'm</b>"
                                   ), parse_mode="HTML"
                                   )



    return ConversationHandler.END


def main():

    application = Application.builder().token("7022978226:AAE4rKcFpb2BYgVbcARPFgYkww5FrUyDPtM").build()

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CommandHandler("menu", menu),
            CommandHandler("contact_us", start),  # Replace "contact_us" with appropriate function
        ],
        states={
            START: [MessageHandler(filters.TEXT, begin)],
            LOCATION: [MessageHandler(filters.TEXT | filters.LOCATION, get_location)],
            ORDER: [MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data)],
            CONTACT: [MessageHandler(filters.CONTACT | filters.TEXT, get_contact)],
            CHECK: [MessageHandler(filters.TEXT, check)],
            PHONE_NUMBER: [MessageHandler(filters.TEXT, phone_number)],
            HISTORY: [MessageHandler(filters.TEXT, history)],
        },
        fallbacks=[],
    )
    application.add_handler(conv_handler)
    # application.start_polling(port=5555)
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
