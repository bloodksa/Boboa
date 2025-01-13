import os
import logging
import datetime
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
Updater, CommandHandler, MessageHandler, Filters, CallbackContext
)
from database import (
get_session, SupportTicket, SupportMessage,
)
logging.basicConfig(level=logging.INFO)
load_dotenv()
SUPPORT_BOT_TOKEN = os.getenv("SUPPORT_BOT_TOKEN", "YOUR_SUPPORT_BOT_TOKEN")
def start_cmd(update: Update, context: CallbackContext):
update.message.reply_text(
"مرحبًا بك في بوت الدعم!\n"
" - /newticket <عنوان> لفتح تذكرة جديدة\n"
" - /mytickets لعرض تذاكرك\n"
" - /closeticket <رقم التذكرة> لإغلاق تذكرة\n"
"ارسل أي رسالة أخرى لإضافتها لآخر تذكرة مفتوحة."
)
def newticket_cmd(update: Update, context: CallbackContext):
user_id = update.effective_user.id
title = " ".join(context.args) if context.args else "No Title"
s = get_session()
ticket = SupportTicket(
user_id=user_id,
title=title
)
s.add(ticket)
s.commit()
s.commit()
s.close()
update.message.reply_text(f"تم فتح تذكرة جديدة رقم
"يمكنك الآن إرسال أي رسائل لشرح مشكلتك.")
def mytickets_cmd(update: Update, context: CallbackContext):
user_id = update.effective_user.id
s = get_session()
tickets = s.query(SupportTicket).filter_by(user_id=user_id).all()
s.close()
if not tickets:
update.message.reply_text("ليس لديك أي تذاكر دعم.")
return
msg = "تذاكرك:\n"
for t in tickets:
msg += f"-
update.message.reply_text(msg)
def closeticket_cmd(update: Update, context: CallbackContext):
user_id = update.effective_user.id
if not context.args:
update.message.reply_text("استخدم: /closeticket <رقم التذكرة>")
return
try:
tid = int(context.args[0])
except:
update.message.reply_text("رقم تذكرة غير صحيح.")
return
s = get_session()
ticket = s.query(SupportTicket).filter_by(id=tid, user_id=user_id).first()
if not ticket:
update.message.reply_text("لا توجد تذكرة بهذا الرقم تخصك.")
s.close()
return
if ticket.status == "closed":
update.message.reply_text("هذه التذكرة مغلقة بالفعل.")
s.close()
return
ticket.status = "closed"
s.commit()
s.close()
update.message.reply_text(f"تم إغلاق التذكرة
def message_handler(update: Update, context: CallbackContext):
"""
نستقبل أي رسالة نصية عادية (ليست أمرًا).
الافتراض: المستخدم يريد إضافتها لآخر تذكرة مفتوحة (إن وجدت).
"""
user_id = update.effective_user.id
text = update.message.text
s = get_session()
ticket = s.query(SupportTicket).filter_by(user_id=user_id, status="open").order_by(SupportTicket.id.desc()).first()
if not ticket:
s.close()
update.message.reply_text("ليس لديك أي تذكرة مفتوحة. استخدم /newticket لفتح تذكرة جديدة.")
return
msg = SupportMessage(
ticket_id=ticket.id,
sender_id=user_id,
text=text
)
s.add(msg)
s.commit()
s.close()
update.message.reply_text(f"تم إضافة رسالتك إلى التذكرة
def admin_listtickets_cmd(update: Update, context: CallbackContext):
"""
يعرض كل التذاكر في النظام (فقط للمشرف).
يمكنك إضافة تحقق admin if statement.
"""
s = get_session()
tickets = s.query(SupportTicket).order_by(SupportTicket.status, SupportTicket.id.desc()).all()
s.close()
msg = "كل التذاكر:\n"
for t in tickets:
msg += f"
update.message.reply_text(msg)
def admin_closeticket_cmd(update: Update, context: CallbackContext):
"""
أمر إداري لإغلاق تذكرة أي مستخدم.
"""
if len(context.args)==0:
update.message.reply_text("استخدم: /admin_closeticket <TicketID>")
return
tid = int(context.args[0])
s = get_session()
ticket = s.query(SupportTicket).filter_by(id=tid).first()
if not ticket:
update.message.reply_text("لا توجد تذكرة بهذا الرقم.")
s.close()
return
ticket.status = "closed"
s.commit()
s.close()
update.message.reply_text(f"تم إغلاق التذكرة
def main():
updater = Updater(SUPPORT_BOT_TOKEN, use_context=True)
dp = updater.dispatcher
dp.add_handler(CommandHandler("start", start_cmd))
dp.add_handler(CommandHandler("newticket", newticket_cmd))
dp.add_handler(CommandHandler("mytickets", mytickets_cmd))
dp.add_handler(CommandHandler("closeticket", closeticket_cmd))
dp.add_handler(CommandHandler("admin_listtickets", admin_listtickets_cmd))
dp.add_handler(CommandHandler("admin_closeticket", admin_closeticket_cmd))
dp.add_handler(MessageHandler(Filters.text & ~Filters.command, message_handler))
updater.start_polling()
updater.idle()
if __name__ == "__main__":
main()
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Command to show help information
def help_cmd(update: Update, context: CallbackContext):
    help_text = (
        "مرحبًا بك في البوت الرئيسي! إليك الأوامر المتاحة:
"
        "/help - عرض قائمة الأوامر
"
        "/newticket - فتح تذكرة دعم
"
        "/mytickets - عرض تذاكرك
"
        "/status - عرض حالة البوت
"
        "/feedback - إرسال ملاحظات
"
    )
    update.message.reply_text(help_text)

# Command to show bot status
def status_cmd(update: Update, context: CallbackContext):
    status_text = "البوت يعمل بشكل طبيعي! 🚀"
    update.message.reply_text(status_text)

# Command to collect feedback
def feedback_cmd(update: Update, context: CallbackContext):
    update.message.reply_text("يرجى كتابة ملاحظاتك:")
    return "COLLECT_FEEDBACK"

# Handler for collecting feedback
def collect_feedback(update: Update, context: CallbackContext):
    feedback = update.message.text
    user = update.effective_user
    # Save feedback to database or log (Mocked here)
    print(f"Feedback from {user.id}: {feedback}")
    update.message.reply_text("شكرًا لك على ملاحظاتك! 🙏")
    return -1

# Inline keyboard for support options
def start_cmd(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("فتح تذكرة", callback_data='new_ticket')],
        [InlineKeyboardButton("عرض التذاكر", callback_data='view_tickets')],
        [InlineKeyboardButton("إرسال ملاحظات", callback_data='send_feedback')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("مرحبًا بك! ماذا تود أن تفعل؟", reply_markup=reply_markup)

# Callback query handler for inline buttons
def handle_callback_query(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    if query.data == 'new_ticket':
        query.edit_message_text(text="يرجى كتابة عنوان التذكرة:")
        return "COLLECT_TICKET_TITLE"
    elif query.data == 'view_tickets':
        query.edit_message_text(text="عرض جميع تذاكرك: (Mock Data)")
    elif query.data == 'send_feedback':
        query.edit_message_text(text="يرجى كتابة ملاحظاتك:")
        return "COLLECT_FEEDBACK"

# Adding the commands to the dispatcher
dispatcher = Updater(SUPPORT_BOT_TOKEN).dispatcher
dispatcher.add_handler(CommandHandler("help", help_cmd))
dispatcher.add_handler(CommandHandler("status", status_cmd))
dispatcher.add_handler(CommandHandler("feedback", feedback_cmd))
dispatcher.add_handler(CallbackQueryHandler(handle_callback_query))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, collect_feedback))

# Function to notify users when a ticket is updated
def notify_ticket_update(user_id, ticket_id, status):
    context = CallbackContext(dispatcher=Updater(SUPPORT_BOT_TOKEN).dispatcher)
    message = f"تم تحديث حالة التذكرة رقم {ticket_id} إلى: {status}"
    try:
        context.bot.send_message(chat_id=user_id, text=message)
    except Exception as e:
        print(f"Error sending notification to user {user_id}: {e}")

# Example integration in the ticket update process (mocked function)
def update_ticket_status(ticket_id, new_status):
    # Mock database query to find ticket and user
    user_id = 123456  # Replace with actual user ID linked to the ticket
    # Update ticket status in the database (mocked)
    print(f"Updating ticket {ticket_id} to status: {new_status}")
    # Notify the user about the update
    notify_ticket_update(user_id, ticket_id, new_status)

# Command to create a poll
def create_poll(update: Update, context: CallbackContext):
    poll_question = "ما رأيك في خدماتنا؟"
    poll_options = ["ممتاز", "جيد", "متوسط", "ضعيف"]
    context.bot.send_poll(
        chat_id=update.effective_chat.id,
        question=poll_question,
        options=poll_options,
        is_anonymous=False,
        allows_multiple_answers=False
    )

# Poll handler to process poll answers
def handle_poll(update: Update, context: CallbackContext):
    poll = update.poll
    print(f"Received poll update: {poll}")

# Poll answer handler to collect individual votes
def handle_poll_answer(update: Update, context: CallbackContext):
    answer = update.poll_answer
    user_id = answer.user.id
    selected_option = answer.option_ids[0]
    print(f"User {user_id} voted for option {selected_option}")

# Adding poll handlers to the dispatcher
dispatcher.add_handler(CommandHandler("createpoll", create_poll))
dispatcher.add_handler(PollHandler(handle_poll))
dispatcher.add_handler(PollAnswerHandler(handle_poll_answer))
