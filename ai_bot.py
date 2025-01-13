
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import openai

# Set OpenAI API Key (use your own key or a free service if available)
openai.api_key = "YOUR_OPENAI_API_KEY"

# Command: /ask - Ask a question to the AI
def ask_ai(update: Update, context: CallbackContext):
    question = ' '.join(context.args)
    if not question:
        update.message.reply_text("يرجى كتابة سؤالك بعد الأمر /ask.")
        return
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=question,
            max_tokens=100
        )
        update.message.reply_text(response.choices[0].text.strip())
    except Exception as e:
        update.message.reply_text(f"تعذر معالجة سؤالك: {e}")

# Start AI Chat Bot
def main():
    updater = Updater("YOUR_AI_BOT_TOKEN")
    dispatcher = updater.dispatcher

    # Add handlers
    dispatcher.add_handler(CommandHandler("ask", ask_ai))

    # Start polling
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()

# Enhanced AI Bot Features

# Summarize text using OpenAI API
def summarize_text(update: Update, context: CallbackContext):
    text_to_summarize = ' '.join(context.args)
    if not text_to_summarize:
        update.message.reply_text("يرجى كتابة النص المراد تلخيصه بعد الأمر /summarize.")
        return
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"Summarize the following text: {text_to_summarize}",
            max_tokens=100
        )
        update.message.reply_text(response.choices[0].text.strip())
    except Exception as e:
        update.message.reply_text(f"تعذر تلخيص النص: {e}")

# Translate text using OpenAI API
def translate_text(update: Update, context: CallbackContext):
    text_to_translate = ' '.join(context.args)
    if not text_to_translate:
        update.message.reply_text("يرجى كتابة النص المراد ترجمته بعد الأمر /translate.")
        return
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"Translate the following text to Arabic: {text_to_translate}",
            max_tokens=100
        )
        update.message.reply_text(response.choices[0].text.strip())
    except Exception as e:
        update.message.reply_text(f"تعذر ترجمة النص: {e}")

# Add the new commands to the dispatcher
dispatcher.add_handler(CommandHandler("summarize", summarize_text))
dispatcher.add_handler(CommandHandler("translate", translate_text))
