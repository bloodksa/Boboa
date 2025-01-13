import os
import logging
import json
from pathlib import Path
from dotenv import load_dotenv
from telegram import (
Update, InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
Updater, CommandHandler, CallbackQueryHandler, CallbackContext
)
from database import (
get_user_state, set_user_stage, set_user_template, clear_user_state,
get_or_create_userinfo, is_user_banned, is_user_admin, has_user_paid,
get_user_bots, set_max_bots
)
load_dotenv()
BOT_TOKEN = os.getenv("MOTHER_BOT_TOKEN", "123456:ABC-DEF")
PORT = int(os.getenv("PORT", "8443"))
RUN_MODE = os.getenv("RUN_MODE", "polling")
logging.basicConfig(level=logging.INFO)
PLUGINS_DIR = Path("plugins")
BOT_LIBRARY = {}
def load_plugins():
library = {}
for folder in PLUGINS_DIR.iterdir():
if folder.is_dir():
info_file = folder / "info.json"
template_file = folder / "bot_template.py"
if info_file.exists() and template_file.exists():
try:
with open(info_file, "r", encoding="utf-8") as f:
meta = json.load(f)
key = folder.name
library[key] = {
"folder": str(folder),
"info": meta
}
logging.info(f"Plugin loaded: {key} - {meta}")
except json.JSONDecodeError as e:
logging.error(f"Invalid JSON in {info_file}: {e}")
else:
logging.warning(f"Missing required files in: {folder}")
logging.info(f"Total plugins loaded: {len(library)}")
return library
def init_library():
global BOT_LIBRARY
BOT_LIBRARY = load_plugins()
logging.info(f"Loaded {len(BOT_LIBRARY)} templates from 'plugins' folder.")
def start_cmd(update: Update, context: CallbackContext):
user_id = update.effective_user.id
get_or_create_userinfo(user_id)
update.message.reply_text(
"مرحباً بك في منصة bebotai!\n"
"تم تطوير هذه المنصة لتكون مجانية، باستثناء بعض البوتات التي تتطلب اشتراكاً.\n"
"سيتم إضافة بوتات جديدة بشكل دوري.\n"
"لاستكشاف البوتات الجاهزة، يمكنك استخدام الأمر /browsebots.\n"
"لشراء باقة مميزة، استخدم الأمر /buy."
)
def browse_cmd(update: Update, context: CallbackContext):
if is_user_banned(update.effective_user.id):
update.message.reply_text("أنت محظور من استخدام هذه الخدمة.")
return
if not BOT_LIBRARY:
update.message.reply_text("لا توجد بوتات في المكتبة حالياً.")
logging.warning("BOT_LIBRARY is empty.")
return
buttons = []
for key, data in BOT_LIBRARY.items():
name = data["info"].get("name", key)
buttons.append([InlineKeyboardButton(name, callback_data=f"show_{key}")])
logging.info(f"Adding bot to buttons: {name}")
update.message.reply_text(
"اختر أحد البوتات:",
reply_markup=InlineKeyboardMarkup(buttons)
)
def library_callback(update: Update, context: CallbackContext):
query = update.callback_query
query.answer()
data = query.data
user_id = query.from_user.id
if is_user_banned(user_id):
query.edit_message_text("أنت محظور.")
return
if data.startswith("show_"):
key = data.replace("show_", "")
if key not in BOT_LIBRARY:
query.edit_message_text("لم أجد هذا البوت.")
return
info = BOT_LIBRARY[key]["info"]
name = info.get("name", key)
desc = info.get("description", "")
version = info.get("version", "1.0")
text = f"*{name} (v{version})*\n\n{desc}"
kbd = [[InlineKeyboardButton("إنشاء هذا البوت", callback_data=f"create_{key}")]]
query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kbd))
def mybots_cmd(update: Update, context: CallbackContext):
user_id = update.effective_user.id
bots = get_user_bots(user_id)
if not bots:
update.message.reply_text("لا تملك أي بوتات.")
return
txt = ""
for b in bots:
txt += f"BotID:{b.id} | Folder:{b.folder_name} | Status:{b.status}\n"
update.message.reply_text(txt)
def stats_cmd(update: Update, context: CallbackContext):
""" يعرض سعة القرص. """
if not is_user_admin(update.effective_user.id):
update.message.reply_text("ليس لديك صلاحية.")
return
import shutil
total, used, free = shutil.disk_usage("/")
total_gb = total // (2**30)
used_gb = used // (2**30)
free_gb = free // (2**30)
msg = (f"Disk usage:\n"
f"Total: {total_gb} GB\n"
f"Used:  {used_gb} GB\n"
f"Free:  {free_gb} GB\n")
update.message.reply_text(msg)
def main():
init_library()
updater = Updater(BOT_TOKEN, use_context=True)
dp = updater.dispatcher
dp.add_handler(CommandHandler("start", start_cmd))
dp.add_handler(CommandHandler("browsebots", browse_cmd))
dp.add_handler(CommandHandler("mybots", mybots_cmd))
dp.add_handler(CommandHandler("stats", stats_cmd))
dp.add_handler(CallbackQueryHandler(library_callback, pattern=r"^(show_|create_)"))
if RUN_MODE == "webhook":
updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=BOT_TOKEN)
updater.idle()
else:
updater.start_polling()
updater.idle()
if __name__ == "__main__":
main()
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from apscheduler.schedulers.background import BackgroundScheduler
import logging

# Initialize logger
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

# Scheduler for scheduled tasks
scheduler = BackgroundScheduler()
scheduler.start()

# Command: /start - Welcome message with buttons
def start_cmd(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("الإعدادات", callback_data='settings')],
        [InlineKeyboardButton("طلب جديد", callback_data='new_request')],
        [InlineKeyboardButton("عرض التقارير", callback_data='reports')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("مرحبًا بك في بوتنا! اختر خيارًا من القائمة:", reply_markup=reply_markup)

# Command: /help - List of commands
def help_cmd(update: Update, context: CallbackContext):
    help_text = (
        "مرحبًا! إليك قائمة الأوامر المتاحة:
"
        "/start - رسالة ترحيب
"
        "/help - عرض الأوامر
"
        "/status - عرض حالة النظام
"
        "/broadcast - إرسال رسالة لجميع المستخدمين (مشرفين فقط)
"
    )
    update.message.reply_text(help_text)

# Command: /status - Check system status
def status_cmd(update: Update, context: CallbackContext):
    status_text = "النظام يعمل بشكل طبيعي! 🚀"
    update.message.reply_text(status_text)

# Command: /broadcast - Send message to all users (Admins only)
def broadcast_cmd(update: Update, context: CallbackContext):
    if update.effective_user.id != 123456:  # Replace with actual admin ID
        update.message.reply_text("هذا الأمر للمشرفين فقط.")
        return
    context.bot.send_message(chat_id=update.effective_chat.id, text="يرجى كتابة الرسالة لإرسالها:")
    return "COLLECT_BROADCAST_MESSAGE"

# Collect broadcast message
def collect_broadcast_message(update: Update, context: CallbackContext):
    message = update.message.text
    # Broadcast message to all users (mocked list of user IDs)
    user_ids = [123, 456, 789]  # Replace with actual user IDs
    for user_id in user_ids:
        try:
            context.bot.send_message(chat_id=user_id, text=message)
        except Exception as e:
            logging.error(f"Failed to send message to user {user_id}: {e}")
    update.message.reply_text("تم إرسال الرسالة لجميع المستخدمين.")
    return -1

# Inline button handler
def handle_inline_buttons(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    if query.data == 'settings':
        query.edit_message_text("خيارات الإعدادات:
- تغيير اللغة
- تعديل الإشعارات")
    elif query.data == 'new_request':
        query.edit_message_text("يرجى كتابة تفاصيل الطلب الجديد.")
    elif query.data == 'reports':
        query.edit_message_text("عرض التقارير:
- تقرير الطلبات
- تقرير الأنشطة")

# Adding the commands to the dispatcher
dispatcher = Updater(MAIN_BOT_TOKEN).dispatcher
dispatcher.add_handler(CommandHandler("start", start_cmd))
dispatcher.add_handler(CommandHandler("help", help_cmd))
dispatcher.add_handler(CommandHandler("status", status_cmd))
dispatcher.add_handler(CommandHandler("broadcast", broadcast_cmd))
dispatcher.add_handler(CallbackQueryHandler(handle_inline_buttons))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, collect_broadcast_message))

# AI Response Handler
def ai_response(update: Update, context: CallbackContext):
    user_message = update.message.text.lower()
    if "مرحبا" in user_message or "hello" in user_message:
        update.message.reply_text("مرحبًا! كيف يمكنني مساعدتك اليوم؟")
    elif "شكرا" in user_message or "thanks" in user_message:
        update.message.reply_text("على الرحب والسعة! إذا كنت بحاجة إلى أي شيء آخر، أخبرني.")
    elif "مشكلة" in user_message or "issue" in user_message:
        update.message.reply_text("يؤسفني سماع ذلك. يرجى وصف المشكلة لمساعدتك.")
    else:
        update.message.reply_text("عذرًا، لم أفهم رسالتك. يمكنك كتابة /help للحصول على قائمة بالأوامر.")

# Add the AI response handler to the dispatcher
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, ai_response))

# Example: Scheduled message to all users
def send_scheduled_message():
    user_ids = [123, 456, 789]  # Replace with actual user IDs
    message = "رسالة مجدولة: تذكير بأمر مهم!"
    for user_id in user_ids:
        try:
            dispatcher.bot.send_message(chat_id=user_id, text=message)
        except Exception as e:
            logging.error(f"Failed to send scheduled message to user {user_id}: {e}")

# Schedule the message to be sent every day at 9:00 AM
scheduler.add_job(send_scheduled_message, 'cron', hour=9, minute=0)
