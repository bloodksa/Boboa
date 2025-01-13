from flask import Flask, render_template, redirect, url_for, request, flash
from database import db, initialize_admin, AdminUser, UserInfo
app = Flask(__name__)

from flask_caching import Cache

cache = Cache(config={
    'CACHE_TYPE': 'RedisCache',
    'CACHE_REDIS_HOST': 'localhost',
    'CACHE_REDIS_PORT': 6379,
    'CACHE_REDIS_DB': 0
})
cache.init_app(app)

from database import bcrypt
bcrypt.init_app(app)

from flask_babel import Babel, _

app.config['BABEL_DEFAULT_LOCALE'] = 'ar'
app.config['BABEL_SUPPORTED_LOCALES'] = ['ar', 'en']

babel = Babel(app)

@babel.localeselector
def get_locale():
    return request.args.get('lang') or 'ar'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/mother_bot.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'
db.init_app(app)
with app.app_context():
db.create_all()
initialize_admin()
@app.route('/')
def home():
    return render_template('index.html')
def index():
return render_template("index.html")
@app.route('/login', methods=['GET', 'POST'])
def login():
if request.method == 'POST':
username = request.form['username']
password = request.form['password']
admin = AdminUser.query.filter_by(username=username).first()
if admin and admin.check_password(password):
flash('تم تسجيل الدخول بنجاح!', 'success')
return redirect(url_for('dashboard'))
else:
flash('اسم المستخدم أو كلمة المرور غير صحيحة.', 'danger')
return render_template("login.html")
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')
def dashboard():
users = UserInfo.query.all()
return render_template("dashboard.html", users=users)
@app.route('/add_user', methods=['POST'])
def add_user():
username = request.form['username']
user = UserInfo(username=username)
db.session.add(user)
db.session.commit()
flash('تم إضافة المستخدم بنجاح!', 'success')
return redirect(url_for('dashboard'))
@app.route('/delete_user/<int:user_id>')
def delete_user(user_id):
user = UserInfo.query.get(user_id)
if user:
db.session.delete(user)
db.session.commit()
flash('تم حذف المستخدم بنجاح!', 'success')
return redirect(url_for('dashboard'))
if __name__ == '__main__':
app.run(debug=True)
@app.route('/tickets')
def tickets():
    return "<h1>صفحة إدارة التذاكر</h1>"

@app.route('/bots')
def bots():
    return "<h1>صفحة إدارة البوتات</h1>"

@app.route('/settings')
def settings():
    return "<h1>صفحة الإعدادات</h1>"

from flask import jsonify

@app.route('/api/users', methods=['GET'])
def api_get_users():
    from database import UserInfo
    users = UserInfo.query.all()
    return jsonify([{
        'id': user.user_id,
        'username': user.username,
        'is_admin': user.is_admin,
        'created_bots': user.created_bots
    } for user in users])

@app.route('/api/tickets', methods=['GET'])
def api_get_tickets():
    from database import SupportTicket
    tickets = SupportTicket.query.all()
    return jsonify([{
        'id': ticket.id,
        'title': ticket.title,
        'user_id': ticket.user_id,
        'status': ticket.status
    } for ticket in tickets])

@app.route('/api/bots', methods=['GET'])
def api_get_bots():
    from database import CreatedBot
    bots = CreatedBot.query.all()
    return jsonify([{
        'id': bot.id,
        'name': bot.name,
        'description': bot.description,
        'status': bot.status
    } for bot in bots])

import os
import shutil
import requests
from flask import request, flash, redirect, url_for

@app.route('/upload_bot', methods=['POST'])
def upload_bot():
    bot_name = request.form['bot_name']
    bot_description = request.form['bot_description']
    bot_file = request.files['bot_file']

    if bot_file and bot_file.filename.endswith('.py'):
        upload_folder = 'plugins'
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, bot_file.filename)
        bot_file.save(file_path)
        flash(f"تم رفع البوت '{bot_name}' بنجاح!", "success")
    else:
        flash("يجب رفع ملف بصيغة Python فقط!", "danger")

    return redirect(url_for('bots'))

@app.route('/add_bot_from_github', methods=['POST'])
def add_bot_from_github():
    github_url = request.form['github_url']
    bot_name = request.form['bot_name']
    upload_folder = 'plugins'
    os.makedirs(upload_folder, exist_ok=True)

    try:
        # Clone the GitHub repository into the plugins directory
        subprocess.run(['git', 'clone', github_url, os.path.join(upload_folder, bot_name)], check=True)
        flash(f"تم إضافة البوت '{bot_name}' بنجاح من GitHub!", "success")
    except Exception as e:
        flash(f"فشل إضافة البوت من GitHub: {e}", "danger")

    return redirect(url_for('bots'))

@app.route('/bots', methods=['GET'])
def bots():
    # Mock data for bots - replace with database integration if necessary
    bots = [
        {'name': 'Bot1', 'description': 'Bot description 1', 'status': 'active'},
        {'name': 'Bot2', 'description': 'Bot description 2', 'status': 'inactive'},
        {'name': 'Bot3', 'description': 'Bot description 3', 'status': 'active'}
    ]
    return render_template('manage_bots.html', bots=bots)

@app.route('/manage_bot', methods=['POST'])
def manage_bot():
    bot_name = request.form['bot_name']
    action = request.form['action']

    if action == 'activate':
        # Logic to activate the bot (e.g., update database)
        flash(f"تم تفعيل البوت '{bot_name}' بنجاح!", "success")
    elif action == 'deactivate':
        # Logic to deactivate the bot
        flash(f"تم تعطيل البوت '{bot_name}' بنجاح!", "warning")
    elif action == 'delete':
        # Logic to delete the bot
        upload_folder = 'plugins'
        bot_path = os.path.join(upload_folder, bot_name)
        if os.path.exists(bot_path):
            shutil.rmtree(bot_path)
            flash(f"تم حذف البوت '{bot_name}' بنجاح!", "danger")
        else:
            flash(f"البوت '{bot_name}' غير موجود!", "danger")
    return redirect(url_for('bots'))
