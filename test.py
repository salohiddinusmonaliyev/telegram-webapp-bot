import json
import logging

from telegram import KeyboardButton, ReplyKeyboardMarkup, Update, WebAppInfo, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


LOCATION = range(1)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Buyurtma berish uchun pastdagi tugmani bosing.",
        reply_markup=ReplyKeyboardMarkup.from_button(
            KeyboardButton(
                text="🛒 Buyurtmma berish",
                web_app=WebAppInfo(url="https://zedpos.pythonanywhere.com/"),
            ), resize_keyboard=True, input_field_placeholder="Buyurtma bering"
        ),
    )


async def web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
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

    await context.bot.send_message(chat_id=6513420947,
                                   text=(
                                       f"<b>Yangi buyurtma 🚚</b>{text}\n\n<b>💰 Umumiy narx: {total_price} so'm</b>"
                                   ), parse_mode="HTML"
                                   )

    await update.message.reply_text(f"{text}\n\n<b>💰 Umumiy narx: {total_price} so'm</b>", parse_mode="HTML")
    await update.message.reply_text("Joylashuvingizni yuboring", reply_markup=ReplyKeyboardMarkup.from_button(
        KeyboardButton(
            text="📍Joylashuvni yuborish", request_location=True
        ), resize_keyboard=True,
    ))

    # return LOCATION


# async def get_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     location = update.message.location
#     await update.message.reply_text("...")
#
#
# async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     await update.message.reply_text(
#         "Bye!", reply_markup=ReplyKeyboardRemove()
#     )
#
#     return ConversationHandler.END

# def main() -> None:
#     """Run the bot."""
#     # Create the Application and pass it your bot's token.
#     application = Application.builder().token("6982793504:AAEUCs6fcuyiD0HbmOkWtO5_SgzdG2ULnfM").build()
#
#     # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
#     conv_handler = ConversationHandler(
#         entry_points=[CommandHandler("start", start)],
#         states={
#             LOCATION: [
#                 MessageHandler(filters.LOCATION, get_location),
#             ],
#         },
#         fallbacks=[CommandHandler("cancel", cancel)],
#     )
#
#     application.add_handler(conv_handler)
#
#     # Run the bot until the user presses Ctrl-C
#     application.run_polling(allowed_updates=Update.ALL_TYPES)

def main() -> None:
    application = Application.builder().token("6982793504:AAEUCs6fcuyiD0HbmOkWtO5_SgzdG2ULnfM").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()