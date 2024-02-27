'''
  For more samples please visit https://github.com/Azure-Samples/cognitive-services-speech-sdk
'''

import azure.cognitiveservices.speech as speechsdk

from telegram import KeyboardButton, ReplyKeyboardMarkup, Update, WebAppInfo, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler


# Creates an instance of a speech config with specified subscription key and service region.
speech_key = "5bab0ec1dc714f80a0e304a855ad398c"
service_region = "eastus2"

GET_TEXT, REPLY_AUDIO = range(2)

async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')

    return REPLY_AUDIO

async def func1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "/start":
      await update.message.reply_text("Matn yuboring")
    else:
      speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
      # Note: the voice setting will not overwrite the voice element in input SSML.
      speech_config.speech_synthesis_voice_name = "uz-UZ-SardorNeural"
      text = f"{update.message.text}"

      # use the default speaker as audio output.
      speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)

      result = speech_synthesizer.speak_text_async(text).get()
      # Check result
      if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
          print("Speech synthesized for text [{}]".format(text))
      elif result.reason == speechsdk.ResultReason.Canceled:
          cancellation_details = result.cancellation_details
          print("Speech synthesis canceled: {}".format(cancellation_details.reason))
          if cancellation_details.reason == speechsdk.CancellationReason.Error:
              print("Error details: {}".format(cancellation_details.error_details))


      speech_config.set_speech_synthesis_output_format(speechsdk.SpeechSynthesisOutputFormat.Riff24Khz16BitMonoPcm)
      speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)

      stream = speechsdk.AudioDataStream(result)
      stream.save_to_wav_file("file.wav")
      await update.message.reply_voice(voice="file.wav")


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("6537176842:AAHA4C1Njv9-_u4by5fOStvw0wHOOjl2O0k").build()

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", hello)],
        states={
            REPLY_AUDIO: [MessageHandler(filters.TEXT, func1)],
        },
        fallbacks=[],
    )
    application.add_handler(conv_handler)
    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()