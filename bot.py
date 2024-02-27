import json
import logging

from telegram import KeyboardButton, ReplyKeyboardMarkup, Update, WebAppInfo, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler

import re
import requests
from datetime import date
from datetime import datetime, timedelta

import pandas as pd

pattern = r'\+998\d{9}\b'

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

START, LOCATION, ORDER, CONTACT, PHONE_NUMBER, PERIOD, HISTORY = range(7)


ADMIN = "6513420947"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if str(update.effective_user.id) == ADMIN:
        await update.message.reply_text("Salom", reply_markup=ReplyKeyboardMarkup(
            [["📄 Buyurtmalar tarixini olish"], ["🛍 Buyurtma berish", "ℹ️ Biz haqimizda"]],
            resize_keyboard=True
        ))
        return START
    else:
        await update.message.reply_text("Salom", reply_markup=ReplyKeyboardMarkup(
            [["🛍 Buyurtma berish", "ℹ️ Biz haqimizda"]],
            resize_keyboard=True
        ))

        return START

async def begin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🛍 Buyurtma berish":
        await update.message.reply_text("Buyurtma berish uchun birinchi navbatda joylashuvingizni yuboring",
                                        reply_markup=ReplyKeyboardMarkup.from_button(
                                            KeyboardButton(
                                                text="📍Joylashuvni yuborish", request_location=True
                                            ), resize_keyboard=True,
                                        ))

    elif update.message.text == "ℹ️ Biz haqimizda":
        await update.message.reply_text("Buyurtma berish uchun /start ni bosing", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    elif update.message.text == "📄 Buyurtmalar tarixini olish":
            await update.message.reply_text("Iltimos, mijoz telefon raqamini kiriting:")
            return PHONE_NUMBER

    elif update.message.text == "/start":
        if str(update.effective_user.id) == ADMIN:
            await update.message.reply_text("Salom", reply_markup=ReplyKeyboardMarkup(
                [["📄 Buyurtmalar tarixini olish"], ["🛍 Buyurtma berish", "ℹ️ Biz haqimizda"]],
                resize_keyboard=True
            ))
            return START
        else:
            await update.message.reply_text("Salom", reply_markup=ReplyKeyboardMarkup(
                [["🛍 Buyurtma berish", "ℹ️ Biz haqimizda"]],
                resize_keyboard=True
            ))

            return START
    else:
        await update.message.reply_text("Buyurtma berish uchun /start ni bosing", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END


    return LOCATION

async def phone_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if re.match(pattern, update.message.text):
        user_data = context.user_data
        user_data["phone_number"] = update.message.text
        await update.message.reply_text("Muddatni tanlang:", reply_markup=ReplyKeyboardMarkup(
                [["Oylik", "Yillik"]]
            , resize_keyboard=True))
        return HISTORY
    else:
        await update.message.reply_html("❌ Iltimos, raqamni <b>+998XXXXXXXXX</b> formatida kiriting.")
        return PHONE_NUMBER

async def history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    json_data = requests.get("https://special-space-adventure-rq799wpxw442xgxr-8000.app.github.dev/api/order/")
    json_data_order_item = requests.get("https://special-space-adventure-rq799wpxw442xgxr-8000.app.github.dev/api/order-item/")
    items = json_data_order_item.json()
    order = json_data.json()
    order_list = []

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


    phone_number = f"{context.user_data['phone_number']}"
    for i in order:
        if i["user"]==phone_number:
            order_list.append(i)
    file_name = f"{phone_number} - {update.message.text} - {date.today()}"

    metadata = ['id', 'time', 'total_price', 'user']

    items = []
    for entry in order_list:
        entry_info = [entry[key] for key in metadata]
        for item in entry['items']:
            items.append(entry_info + [item[key] for key in item])

    df = pd.DataFrame(items, columns=metadata + list(entry['items'][0].keys()))
    excel_filename = f'history/{file_name}.xlsx'
    df.to_excel(excel_filename, index=False)
    await update.message.reply_document(document=f"history/{file_name}.xlsx", caption=f"<b>📄 Buyurtmalar tarixi</b>\n\n👤 Foydalanuvchi: {context.user_data['phone_number']}\n<b>📅 {update.message.text}</b>", parse_mode="HTML", reply_markup=ReplyKeyboardRemove())


    today = datetime.now()

    # Calculate the first day of the previous month
    first_day_previous_month = today.replace(day=1) - timedelta(days=1)
    first_day_previous_month = first_day_previous_month.replace(day=1)

    # Initialize an empty list to store items from the last month
    last_month_items = []

    # Iterate through data
    for entry in order_list:
        # Convert time string to datetime object
        entry_time = datetime.strptime(entry['time'], '%Y-%m-%d')

        # Check if the entry's time is in the previous month
        if first_day_previous_month <= entry_time <= today.replace(day=1):
            last_month_items.extend(entry['items'])

    # Print or process last month items as needed
    print(last_month_items)




    return ConversationHandler.END


async def get_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
                web_app=WebAppInfo(url="https://special-space-adventure-rq799wpxw442xgxr-8000.app.github.dev/"),
            ), resize_keyboard=True, input_field_placeholder="Buyurtma bering"
        ),
    )

    return ORDER


async def web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> range:
    global data

    data = json.loads(update.effective_message.web_app_data.data)
    text = ""
    total_price = 0
    for i in data:
        if i["quantity"] != 0 and i['quantity'] is not None:
            totalprice = int(i["quantity"]) * float(i["price"])
            total_price += totalprice
            totalprice = "{:,.0f}".format(totalprice).replace(",", " ")
            text = (f"{text}\n\n👉 Mahsulot nomi: {i['title']}\nMiqdori: {i['quantity']} dona"
                    f"\nBir dona mahsulot narxi: {i['price']} so'm\nUmumiy narx: {totalprice} so'm")

    total_price = "{:,.0f}".format(total_price).replace(",", " ")

    await update.message.reply_text(f"{text}\n\n<b>💰 Umumiy narx: {total_price} so'm</b>", parse_mode="HTML")

    await update.message.reply_text("✅ Buyurtmalar qabul qilindi\n\nTelefon raqamingizni joꞌnating. \n(<b>☎️ Telefon raqamni yuborish</b> tugmasini bosing Yoki raqamingizni quyidagi formatda kiriting (<b>+998xxxxxxxxx</b>)", parse_mode="HTML",reply_markup=ReplyKeyboardMarkup.from_button(
        KeyboardButton(
            text="☎️ Telefon raqamni yuborish", request_contact=True
        ), resize_keyboard=True
    ))

    global order_items
    global order_total_price
    order_total_price = total_price

    order_items = text

    return CONTACT

async def get_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global contact
    if update.message.contact:
        contact = update.message.contact.phone_number
    else:
        contact = update.message.text
        if re.match(pattern, contact):
            await update.message.reply_text("✅ Telefon raqam qabul qilindi", reply_markup=ReplyKeyboardRemove())
            contact = update.message.text
        else:
            await update.message.reply_text("❌ Iltimos, raqamingizni quyidagi formatda kiriting (<b>+998xxxxxxxxx</b>)", parse_mode="HTML")
            return CONTACT
    user_data = f"{order_items}\n\n<b>☎️ Telefon raqam: {contact}</b>\n<b>📍 Manzil: {user_location}</b>"

    await context.bot.send_message(chat_id=6513420947,
                                   text=(
                                       f"<b>Yangi buyurtma 🚚</b>{user_data}\n\n<b>💰 Umumiy narx: {order_total_price} so'm</b>"
                                   ), parse_mode="HTML"
                                   )

    json_data = {
        "time": f"{date.today()}",
        "description": "none",
        "total_price": order_total_price,
        "user": f"{contact}"
    }


    order_response = requests.post(url="https://special-space-adventure-rq799wpxw442xgxr-8000.app.github.dev/api/order/", json=json_data)

    for i in data:
        order_item_data = {
            "order_id": order_response.json()["id"],
            "price": i["price"],
            "quantity": i["quantity"],
            "product": i["id"],
        }
        order_item_response = requests.post(url="https://special-space-adventure-rq799wpxw442xgxr-8000.app.github.dev/api/order-item/", json=order_item_data)


    await update.message.reply_text("Buyurtma qabul qilindi. Tez orada siz bilan bo'glanishadi.",
                                    reply_markup=ReplyKeyboardRemove())

    await update.message.reply_text("Yangi buyurtma berish uchun <b>/start</b> ni bosing", reply_markup=ReplyKeyboardRemove(), parse_mode="HTML")


    return ConversationHandler.END

def main() -> None:
    """Run the bot."""
    application = Application.builder().token("6700413743:AAHlpPDdkrG5AspzykFomQP3EpKy_7WTNfo").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            START: [MessageHandler(filters.TEXT, begin)],
            LOCATION: [MessageHandler(filters.TEXT, get_location),
                       MessageHandler(filters.LOCATION, get_location)],
            ORDER: [MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data)],
            CONTACT: [MessageHandler(filters.CONTACT, get_contact),
                      MessageHandler(filters.TEXT, get_contact)],
            PHONE_NUMBER: [MessageHandler(filters.TEXT, phone_number)],
            HISTORY: [MessageHandler(filters.TEXT, history)],

        },
        fallbacks=[],
    )
    application.add_handler(conv_handler)
    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()