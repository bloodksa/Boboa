
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Command: /testsite - Test a website
def test_site(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("يرجى كتابة عنوان الموقع بعد الأمر /testsite.")
        return
    url = context.args[0]
    if not url.startswith("http"):
        url = "http://" + url
    try:
        response = requests.get(url, timeout=5)
        update.message.reply_text(
            f"📊 اختبار الموقع: {url}
"
            f"الحالة: {response.status_code}
"
            f"وقت الاستجابة: {response.elapsed.total_seconds()} ثانية."
        )
    except Exception as e:
        update.message.reply_text(f"❌ فشل اختبار الموقع: {e}")

# Start Website Testing Bot
def main():
    updater = Updater("YOUR_WEBSITE_BOT_TOKEN")
    dispatcher = updater.dispatcher

    # Add handlers
    dispatcher.add_handler(CommandHandler("testsite", test_site))

    # Start polling
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()

import csv
from io import StringIO

# Generate a performance report
def generate_report(update: Update, context: CallbackContext):
    urls = context.args
    if not urls:
        update.message.reply_text("يرجى إدخال روابط المواقع المراد فحصها بعد الأمر /report.")
        return

    report_data = []
    for url in urls:
        if not url.startswith("http"):
            url = "http://" + url
        try:
            response = requests.get(url, timeout=5)
            report_data.append({
                "URL": url,
                "Status Code": response.status_code,
                "Response Time (s)": response.elapsed.total_seconds()
            })
        except Exception as e:
            report_data.append({"URL": url, "Error": str(e)})

    # Generate CSV report
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=["URL", "Status Code", "Response Time (s)", "Error"])
    writer.writeheader()
    writer.writerows(report_data)
    output.seek(0)

    # Send the CSV file to the user
    update.message.reply_document(
        document=output.getvalue(),
        filename="website_report.csv",
        caption="تقرير أداء المواقع"
    )

# Add the new command to the dispatcher
dispatcher.add_handler(CommandHandler("report", generate_report))
