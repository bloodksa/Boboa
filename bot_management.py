
from flask import Flask, render_template, request, redirect, url_for, flash
import subprocess

app = Flask(__name__)
app.secret_key = 'super_secret_key'

# Mock data for bots (Replace with database later)
bots = [
    {"name": "Security Bot", "file": "security_bot.py", "status": "stopped"},
    {"name": "AI Chat Bot", "file": "ai_bot.py", "status": "stopped"},
    {"name": "Website Testing Bot", "file": "website_testing_bot.py", "status": "stopped"},
    {"name": "Broadcast Bot", "file": "broadcast_bot.py", "status": "stopped"},
]

# Start a bot
def start_bot(bot_file):
    try:
        subprocess.Popen(["python", bot_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except Exception as e:
        print(f"Error starting bot {bot_file}: {e}")
        return False

# Stop a bot (Mock implementation for now)
def stop_bot(bot_name):
    # Implement proper process management
    return True

@app.route('/')
def index():
    return render_template('index.html', bots=bots)

@app.route('/start_bot/<bot_name>')
def start_bot_route(bot_name):
    bot = next((b for b in bots if b["name"] == bot_name), None)
    if bot and start_bot(bot["file"]):
        bot["status"] = "running"
        flash(f"{bot_name} started successfully!", "success")
    else:
        flash(f"Failed to start {bot_name}.", "danger")
    return redirect(url_for('index'))

@app.route('/stop_bot/<bot_name>')
def stop_bot_route(bot_name):
    bot = next((b for b in bots if b["name"] == bot_name), None)
    if bot and stop_bot(bot_name):
        bot["status"] = "stopped"
        flash(f"{bot_name} stopped successfully!", "success")
    else:
        flash(f"Failed to stop {bot_name}.", "danger")
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)

from celery_config import celery

# Example task to send a broadcast message
@celery.task
def broadcast_message_task(message, user_ids):
    for user_id in user_ids:
        try:
            # Replace with actual bot send_message logic
            print(f"Sending message to {user_id}: {message}")
        except Exception as e:
            print(f"Failed to send message to {user_id}: {e}")

@app.route('/broadcast', methods=['POST'])
def broadcast():
    message = request.form['message']
    user_ids = [123456, 789012, 345678]  # Mocked list of user IDs
    broadcast_message_task.delay(message, user_ids)
    flash("تم إرسال الرسالة لجميع المستخدمين عبر المهام الخلفية!", "success")
    return redirect(url_for('index'))

# Mock database for user settings (Replace with real database later)
user_settings = {
    123456: {"language": "ar", "notifications": True},
    789012: {"language": "en", "notifications": False},
}

@app.route('/settings/<int:user_id>', methods=['GET', 'POST'])
def manage_settings(user_id):
    if request.method == 'POST':
        language = request.form['language']
        notifications = request.form.get('notifications') == 'on'
        # Update settings in the mock database
        user_settings[user_id] = {"language": language, "notifications": notifications}
        flash("تم تحديث الإعدادات بنجاح!", "success")
        return redirect(url_for('manage_settings', user_id=user_id))

    # Fetch user settings (Mocked for now)
    settings = user_settings.get(user_id, {"language": "ar", "notifications": True})
    return render_template('settings.html', user_id=user_id, settings=settings)

from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'super_secret_key'

# Mocked list of available bots
bots = [
    {"name": "Security Bot", "description": "بوت لحماية المجموعات من الرسائل غير المرغوب فيها."},
    {"name": "AI Assistant Bot", "description": "بوت ذكي للإجابة على الأسئلة وتقديم المساعدة."},
    {"name": "Website Testing Bot", "description": "بوت لاختبار المواقع وتحليل الأداء."},
    {"name": "Broadcast Bot", "description": "بوت لإرسال الإعلانات والرسائل الجماعية."}
]

# Mocked user bot configurations (Replace with a real database later)
user_bot_configurations = {}

@app.route('/select_bots', methods=['GET'])
def select_bots():
    return render_template('select_bots.html', bots=bots)

@app.route('/configure_bot', methods=['POST'])
def configure_bot():
    bot_name = request.form['bot_name']
    return render_template('configure_bot.html', bot_name=bot_name)

@app.route('/activate_bot', methods=['POST'])
def activate_bot():
    bot_name = request.form['bot_name']
    token = request.form['token']

    # Store the token and mark the bot as active (Mock implementation)
    user_bot_configurations[bot_name] = {"token": token, "status": "active"}
    flash(f"تم تفعيل البوت '{bot_name}' بنجاح باستخدام التوكن!", "success")
    return redirect(url_for('select_bots'))

if __name__ == "__main__":
    app.run(debug=True)

import datetime

# Mock database for bot statuses and logs
bot_statuses = {
    "Security Bot": {"status": "stopped", "last_updated": None},
    "AI Assistant Bot": {"status": "stopped", "last_updated": None},
    "Website Testing Bot": {"status": "stopped", "last_updated": None},
    "Broadcast Bot": {"status": "stopped", "last_updated": None},
}

bot_logs = []

@app.route('/advanced_bots', methods=['GET', 'POST'])
def advanced_bots():
    if request.method == 'POST':
        action = request.form.get('action')
        bot_name = request.form.get('bot_name')

        if action == 'start':
            bot_statuses[bot_name]["status"] = "running"
            bot_statuses[bot_name]["last_updated"] = datetime.datetime.now()
            bot_logs.append(f"{bot_name} started at {datetime.datetime.now()}")
        elif action == 'stop':
            bot_statuses[bot_name]["status"] = "stopped"
            bot_statuses[bot_name]["last_updated"] = datetime.datetime.now()
            bot_logs.append(f"{bot_name} stopped at {datetime.datetime.now()}")

        flash(f"{bot_name} {action}ed successfully!", "success")
        return redirect(url_for('advanced_bots'))

    return render_template('advanced_bots.html', bot_statuses=bot_statuses, bot_logs=bot_logs)

from flask import session
import requests

# Mock database for users
users = {
    "admin": {"password": "admin123", "2fa": "123456"}
}

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        otp = request.form.get('otp')

        # Validate username and password
        user = users.get(username)
        if user and user['password'] == password:
            # Validate 2FA if enabled
            if user.get('2fa') and otp != user['2fa']:
                flash("رمز المصادقة الثنائية غير صحيح.", "danger")
                return redirect(url_for('login'))

            session['user'] = username
            flash("تم تسجيل الدخول بنجاح!", "success")
            return redirect(url_for('advanced_bots'))

        flash("اسم المستخدم أو كلمة المرور غير صحيحة.", "danger")
        return redirect(url_for('login'))

    return render_template('login.html')

# Logout route
@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("تم تسجيل الخروج بنجاح.", "success")
    return redirect(url_for('login'))

# Token verification for bots
def verify_token(token):
    try:
        response = requests.get(f"https://api.telegram.org/bot{token}/getMe")
        return response.status_code == 200
    except Exception as e:
        return False

@app.route('/activate_bot', methods=['POST'])
def activate_bot_with_verification():
    bot_name = request.form['bot_name']
    token = request.form['token']

    # Verify token
    if not verify_token(token):
        flash("التوكن غير صالح. يرجى التحقق وإعادة المحاولة.", "danger")
        return redirect(url_for('configure_bot', bot_name=bot_name))

    # Store the token and mark the bot as active (Mock implementation)
    user_bot_configurations[bot_name] = {"token": token, "status": "active"}
    flash(f"تم تفعيل البوت '{bot_name}' بنجاح باستخدام التوكن!", "success")
    return redirect(url_for('select_bots'))

# Mocked subscription data (Replace with real database later)
subscriptions = {
    "basic": {"price": 10, "features": ["5 بوتات", "50 رسالة يوميًا"]},
    "premium": {"price": 30, "features": ["10 بوتات", "500 رسالة يوميًا", "تقارير مفصلة"]},
    "enterprise": {"price": 100, "features": ["بوتات غير محدودة", "رسائل غير محدودة", "تقارير متقدمة", "دعم 24/7"]}
}

user_subscriptions = {}

@app.route('/subscriptions', methods=['GET', 'POST'])
def manage_subscriptions():
    if request.method == 'POST':
        plan = request.form['plan']
        user_subscriptions[session.get('user', 'guest')] = plan
        flash(f"تم الاشتراك في خطة {plan} بنجاح!", "success")
        return redirect(url_for('manage_subscriptions'))

    return render_template('subscriptions.html', subscriptions=subscriptions, user_subscriptions=user_subscriptions)

@app.route('/store', methods=['GET'])
def store():
    return render_template('store.html')

# Update subscription plans to include trial periods and custom plans
@app.route('/subscriptions', methods=['GET', 'POST'])
def manage_subscriptions():
    trial_enabled = True  # Enable trial period for all plans
    if request.method == 'POST':
        plan = request.form['plan']
        if trial_enabled:
            flash(f"تم تفعيل فترة تجريبية مجانية لخطة {plan}!", "success")
        user_subscriptions[session.get('user', 'guest')] = plan
        flash(f"تم الاشتراك في خطة {plan} بنجاح!", "success")
        return redirect(url_for('manage_subscriptions'))

    return render_template(
        'subscriptions.html',
        subscriptions=subscriptions,
        user_subscriptions=user_subscriptions,
        trial_enabled=trial_enabled
    )

import random

# Mocked user activity data
user_activity = {
    "Security Bot": {"messages_sent": 120, "active_users": 40},
    "AI Bot": {"messages_sent": 150, "active_users": 60},
    "Testing Bot": {"messages_sent": 90, "active_users": 20},
    "Broadcast Bot": {"messages_sent": 200, "active_users": 80},
}

# AI-based recommendation route
@app.route('/recommendations', methods=['GET'])
def recommendations():
    recommendations = []

    # Generate recommendations based on activity
    for bot, data in user_activity.items():
        if data["messages_sent"] > 100:
            recommendations.append(f"زيادة ميزانية الرسائل لبوت {bot} بسبب نشاطه العالي.")
        if data["active_users"] > 50:
            recommendations.append(f"قد تحتاج إلى خطة متميزة لدعم المستخدمين النشطين في {bot}.")
    
    # Random tip for diversity
    tips = [
        "جرب تقارير الأداء الأسبوعية لتحليل أفضل.",
        "تفعيل الرسائل المجدولة يمكن أن يحسن تفاعل المستخدمين.",
        "استخدام التخزين المؤقت (Caching) لتسريع الأداء."
    ]
    recommendations.append(random.choice(tips))

    return render_template('recommendations.html', recommendations=recommendations)

import os

# Mocked database for user-created bots (Replace with real DB later)
user_created_bots = {}

@app.route('/create_bot', methods=['GET', 'POST'])
def create_bot():
    if request.method == 'POST':
        bot_name = request.form['bot_name']
        bot_description = request.form['bot_description']
        language = request.form['language']
        unlimited_messages = 'unlimited_messages' in request.form
        gpt_4 = 'gpt_4' in request.form

        # Save bot configuration
        bot_id = len(user_created_bots) + 1
        user_created_bots[bot_id] = {
            "name": bot_name,
            "description": bot_description,
            "language": language,
            "unlimited_messages": unlimited_messages,
            "gpt_4": gpt_4,
            "status": "inactive"
        }

        # Create a placeholder file for the bot (simulate deployment)
        bot_file_path = os.path.join('user_bots', f"{bot_name}.py")
        with open(bot_file_path, 'w', encoding='utf-8') as bot_file:
            bot_file.write(f"# Bot Name: {bot_name}\n")
            bot_file.write(f"# Description: {bot_description}\n")
            bot_file.write(f"# Language: {language}\n")
            bot_file.write(f"# Features: {'Unlimited Messages' if unlimited_messages else ''}, {'GPT-4' if gpt_4 else 'Standard'}\n")

        flash(f"تم إنشاء البوت '{bot_name}' بنجاح!", "success")
        return redirect(url_for('manage_user_bots'))

    return render_template('create_bot.html')

@app.route('/manage_user_bots', methods=['GET'])
def manage_user_bots():
    return render_template('manage_user_bots.html', user_created_bots=user_created_bots)

import subprocess

# Function to start a bot dynamically
def start_bot(bot_name):
    bot_file = os.path.join('user_bots', f"{bot_name}.py")
    if os.path.exists(bot_file):
        process = subprocess.Popen(['python3', bot_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return process
    return None

# Update bot management route to support starting and stopping bots
@app.route('/manage_user_bots', methods=['GET', 'POST'])
def manage_user_bots():
    if request.method == 'POST':
        action = request.form['action']
        bot_id = int(request.form['bot_id'])
        bot_info = user_created_bots.get(bot_id)

        if action == 'start' and bot_info:
            process = start_bot(bot_info['name'])
            if process:
                bot_info['status'] = 'active'
                flash(f"تم تشغيل البوت '{bot_info['name']}' بنجاح!", "success")
            else:
                flash(f"تعذر تشغيل البوت '{bot_info['name']}'.", "danger")
        elif action == 'stop' and bot_info:
            bot_info['status'] = 'inactive'
            flash(f"تم إيقاف البوت '{bot_info['name']}' بنجاح!", "success")

    return render_template('manage_user_bots.html', user_created_bots=user_created_bots)

# Update subscription plans with premium bot pricing
premium_bot_plans = {
    "basic": {"price": 10, "bots": 1, "messages_per_day": 50, "premium_support": False},
    "premium": {"price": 30, "bots": 5, "messages_per_day": 500, "premium_support": True},
    "enterprise": {"price": 100, "bots": 20, "messages_per_day": "unlimited", "premium_support": True},
}

@app.route('/bot_pricing', methods=['GET', 'POST'])
def bot_pricing():
    if request.method == 'POST':
        plan = request.form['plan']
        bot_id = int(request.form['bot_id'])
        bot_info = user_created_bots.get(bot_id)

        # Check if the bot is eligible for the selected plan
        if plan in premium_bot_plans:
            user_created_bots[bot_id]["plan"] = plan
            flash(f"تم تعيين خطة {plan} للبوت '{bot_info['name']}' بنجاح!", "success")
        else:
            flash("الخطة المحددة غير متوفرة.", "danger")

    return render_template('bot_pricing.html', premium_bot_plans=premium_bot_plans, user_created_bots=user_created_bots)

# Mocked database for bot customizations
bot_customizations = {}

@app.route('/customize_bot/<int:bot_id>', methods=['GET', 'POST'])
def customize_bot(bot_id):
    bot_info = user_created_bots.get(bot_id)
    if not bot_info:
        flash("البوت غير موجود.", "danger")
        return redirect(url_for('manage_user_bots'))

    if request.method == 'POST':
        # Save custom rules
        custom_responses = request.form.getlist('custom_responses')
        blocked_words = request.form.getlist('blocked_words')

        # Save customizations
        bot_customizations[bot_id] = {
            "custom_responses": custom_responses,
            "blocked_words": blocked_words
        }
        flash(f"تم تحديث إعدادات البوت '{bot_info['name']}' بنجاح!", "success")
        return redirect(url_for('manage_user_bots'))

    return render_template('customize_bot.html', bot_info=bot_info, bot_customizations=bot_customizations.get(bot_id, {}))

@app.route('/activate_bot', methods=['POST'])
def activate_bot_with_encryption():
    bot_name = request.form['bot_name']
    token = request.form['token']

    # Encrypt the token before saving
    encrypted_token = encrypt_token(token)

    # Store the encrypted token
    user_bot_configurations[bot_name] = {"token": encrypted_token, "status": "active"}
    flash(f"تم تفعيل البوت '{bot_name}' بنجاح باستخدام التوكن المشفر!", "success")
    return redirect(url_for('select_bots'))

# Example route to display decrypted token (admin-only functionality)
@app.route('/view_token/<bot_name>', methods=['GET'])
def view_encrypted_token(bot_name):
    bot_config = user_bot_configurations.get(bot_name)
    if bot_config:
        encrypted_token = bot_config['token']
        decrypted_token = decrypt_token(encrypted_token)
        return f"Encrypted Token: {encrypted_token}<br>Decrypted Token: {decrypted_token}"
    return "Bot not found", 404

@app.route('/analyze_text', methods=['POST'])
def analyze_text():
    user_input = request.form['user_input']
    analysis = TextBlob(user_input)
    polarity = analysis.sentiment.polarity
    subjectivity = analysis.sentiment.subjectivity

    # Determine sentiment type
    if polarity > 0:
        sentiment = "إيجابي"
    elif polarity < 0:
        sentiment = "سلبي"
    else:
        sentiment = "محايد"

    return render_template('text_analysis.html', input=user_input, polarity=polarity, subjectivity=subjectivity, sentiment=sentiment)
