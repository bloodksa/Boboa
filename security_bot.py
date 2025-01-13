
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# List of banned words
BANNED_WORDS = ["spam", "scam", "badword"]

# Command: /ban - Ban a user (Admin only)
def ban_user(update: Update, context: CallbackContext):
    if update.effective_user.id != 123456:  # Replace with admin ID
        update.message.reply_text("هذا الأمر مخصص للمشرفين فقط.")
        return
    try:
        target_user = update.message.reply_to_message.from_user.id
        context.bot.kick_chat_member(chat_id=update.effective_chat.id, user_id=target_user)
        update.message.reply_text("تم حظر المستخدم بنجاح.")
    except Exception as e:
        update.message.reply_text(f"تعذر حظر المستخدم: {e}")

# Message handler: Check for banned words
def check_messages(update: Update, context: CallbackContext):
    message_text = update.message.text.lower()
    if any(word in message_text for word in BANNED_WORDS):
        update.message.delete()
        update.message.reply_text("🚨 تم حذف الرسالة لأنها تحتوي على كلمات محظورة. 🚨")

# Start Security Bot
def main():
    updater = Updater("YOUR_SECURITY_BOT_TOKEN")
    dispatcher = updater.dispatcher

    # Add handlers
    dispatcher.add_handler(CommandHandler("ban", ban_user))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, check_messages))

    # Start polling
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()

# Enhanced Security Bot Features

# Advanced pattern detection for spam or abusive messages
def detect_patterns(update: Update, context: CallbackContext):
    message_text = update.message.text.lower()
    user_id = update.effective_user.id
    if any(word in message_text for word in BANNED_WORDS):
        update.message.delete()
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"🚨 رسالة من المستخدم {user_id} تم حذفها بسبب الكلمات المحظورة 🚨"
        )
        # Notify admin about the deleted message
        admin_id = 123456  # Replace with actual admin ID
        context.bot.send_message(
            chat_id=admin_id,
            text=f"🚨 المستخدم {user_id} حاول إرسال رسالة محظورة: {message_text}"
        )

# Replace the original message handler with the advanced one
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, detect_patterns))
