import json
import logging

from telegram import KeyboardButton, ReplyKeyboardMarkup, Update, WebAppInfo, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

START, LOCATION, ORDER, CONTACT = range(4)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hi! I'm Fastfood delivery bot, I will help you", reply_markup=ReplyKeyboardMarkup(
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
    else:
        await update.message.reply_text("Buyurtma berish uchun /start ni bosing", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    return LOCATION


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
                web_app=WebAppInfo(url="https://zedpos.pythonanywhere.com/"),
            ), resize_keyboard=True, input_field_placeholder="Buyurtma bering"
        ),
    )

    return ORDER


async def web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> range:
    data = json.loads(update.effective_message.web_app_data.data)
    text = ""
    total_price = 0

    for i in data:
        if i["quantity"] != 0 and i['quantity'] is not None:
            totalprice = int(i["quantity"]) * float(i["price"])
            total_price += totalprice
            totalprice = "{:,.0f}".format(totalprice).replace(",", " ")
            text = (f"{text}\n\n👉 Mahsulot kodi: {i['id']}\nMahsulot nomi: {i['title']}\nMiqdori: {i['quantity']} dona"
                    f"\nBir dona mahsulot narxi: {i['price']} so'm\nUmumiy narx: {totalprice} so'm")

    total_price = "{:,.0f}".format(total_price).replace(",", " ")

    await update.message.reply_text(f"{text}\n\n<b>💰 Umumiy narx: {total_price} so'm</b>", parse_mode="HTML")

    await update.message.reply_text("✅ Buyurtmalar qabul qilindi", reply_markup=ReplyKeyboardMarkup.from_button(
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
    contact = update.message.contact
    await update.message.reply_text("✅ Telefon raqam qabul qilindi", reply_markup=ReplyKeyboardRemove())

    user_data = f"{order_items}\n\n<b>☎️ Telefon raqam: {contact.phone_number}</b>\n<b>📍 Manzil: {user_location}</b>"
    await context.bot.send_message(chat_id=6513420947,
                                   text=(
                                       f"<b>Yangi buyurtma 🚚</b>{user_data}\n\n<b>💰 Umumiy narx: {order_total_price} so'm</b>"
                                   ), parse_mode="HTML"
                                   )
    await update.message.reply_text("Yangi buyurtma berish uchun /start ni bosing", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("6264932721:AAFyfzUHWaY96_A9EvJ6hcM92fW_meVR72o").build()

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            START: [MessageHandler(filters.TEXT, begin)],
            LOCATION: [MessageHandler(filters.TEXT, get_location),
                       MessageHandler(filters.LOCATION, get_location)],
            ORDER: [MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data)],
            CONTACT: [MessageHandler(filters.CONTACT, get_contact)],
        },
        fallbacks=[],
    )
    application.add_handler(conv_handler)
    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
