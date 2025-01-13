
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Mocked list of user IDs (replace with actual user database)
USER_IDS = [123456, 789012, 345678]

# Command: /broadcast - Broadcast a message to all users
def broadcast(update: Update, context: CallbackContext):
    if update.effective_user.id != 123456:  # Replace with admin ID
        update.message.reply_text("هذا الأمر مخصص للمشرفين فقط.")
        return
    message = ' '.join(context.args)
    if not message:
        update.message.reply_text("يرجى كتابة الرسالة بعد الأمر /broadcast.")
        return
    for user_id in USER_IDS:
        try:
            context.bot.send_message(chat_id=user_id, text=message)
        except Exception as e:
            update.message.reply_text(f"❌ تعذر إرسال الرسالة للمستخدم {user_id}: {e}")
    update.message.reply_text("✅ تم إرسال الرسالة لجميع المستخدمين.")

# Start Broadcast Bot
def main():
    updater = Updater("YOUR_BROADCAST_BOT_TOKEN")
    dispatcher = updater.dispatcher

    # Add handlers
    dispatcher.add_handler(CommandHandler("broadcast", broadcast))

    # Start polling
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()

import datetime
from collections import defaultdict

# Mocked database for user interaction analytics
interaction_data = defaultdict(int)

# Send a broadcast message and log interactions
def broadcast_with_tracking(update: Update, context: CallbackContext):
    if update.effective_user.id != 123456:  # Replace with admin ID
        update.message.reply_text("هذا الأمر مخصص للمشرفين فقط.")
        return
    message = ' '.join(context.args)
    if not message:
        update.message.reply_text("يرجى كتابة الرسالة بعد الأمر /broadcast.")
        return

    # Mocked list of user IDs
    user_ids = [123456, 789012, 345678]
    for user_id in user_ids:
        try:
            sent_message = context.bot.send_message(chat_id=user_id, text=message)
            interaction_data[sent_message.message_id] = {"user_id": user_id, "status": "sent", "timestamp": datetime.datetime.now()}
        except Exception as e:
            update.message.reply_text(f"تعذر إرسال الرسالة للمستخدم {user_id}: {e}")

    update.message.reply_text("✅ تم إرسال الرسالة مع تسجيل التفاعل.")

# Generate interaction analytics report
def interaction_report(update: Update, context: CallbackContext):
    report = "📊 تقرير التفاعل مع الإعلانات:
"
    for message_id, data in interaction_data.items():
        report += f"- المستخدم {data['user_id']} استلم الرسالة في {data['timestamp']}
"
    update.message.reply_text(report or "لا توجد بيانات تفاعل حتى الآن.")

# Add new commands to the dispatcher
dispatcher.add_handler(CommandHandler("broadcast", broadcast_with_tracking))
dispatcher.add_handler(CommandHandler("interactions", interaction_report))
