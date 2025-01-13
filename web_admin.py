import os
import json
import uuid
from flask import Flask, render_template, redirect, url_for, request, flash, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import subprocess
from flask_talisman import Talisman
from database import db, AdminUser, UserInfo, CreatedBot, SupportTicket, SupportMessage, Ad, initialize_admin
load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("FLASK_SECRET_KEY", "your_secure_secret_key")
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URI", "sqlite:///data/mother_bot.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'plugins/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
csp = {
'default-src': [
'\'self\'',
'maxcdn.bootstrapcdn.com',
'cdnjs.cloudflare.com'
]
}
Talisman(app, content_security_policy=csp)
db.init_app(app)
with app.app_context():
db.create_all()
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
class LoginForm(FlaskForm):
username = StringField('اسم المستخدم', validators=[DataRequired(), Length(min=4, max=150)])
password = PasswordField('كلمة المرور', validators=[DataRequired(), Length(min=4, max=150)])
submit = SubmitField('تسجيل الدخول')
class UploadBotForm(FlaskForm):
name = StringField('اسم البوت', validators=[DataRequired(), Length(min=2, max=150)])
description = StringField('وصف البوت', validators=[DataRequired(), Length(min=5, max=300)])
version = StringField('الإصدار', validators=[DataRequired(), Length(min=1, max=50)])
entry_point = StringField('نقطة الدخول (ملف البوت)', validators=[DataRequired(), Length(min=1, max=100)])
premium_only = BooleanField('مخصص للمستخدمين المدفوعين؟')
bot_file = FileField('رفع ملف البوت (bot.py)')
info_file = FileField('رفع ملف المعلومات (info.json)')
user = SelectField('تعيين البوت لمستخدم', coerce=int, choices=[])
submit = SubmitField('رفع البوت')
class AddAdForm(FlaskForm):
ad_content = StringField('محتوى الإعلان', validators=[DataRequired(), Length(min=5, max=500)])
active = BooleanField('تفعيل الإعلان؟')
submit = SubmitField('إضافة/تعديل الإعلان')
@login_manager.user_loader
def load_user(user_id):
return AdminUser.query.get(int(user_id))
ALLOWED_EXTENSIONS = {'py', 'json'}
def allowed_file(filename):
"""
التحقق مما إذا كان الملف المرفوع يمتلك امتدادًا مسموحًا به.
"""
return '.' in filename and \
filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
def generate_unique_filename(filename):
"""
إنشاء اسم ملف فريد لتجنب التعارضات الأمنية.
"""
ext = filename.rsplit('.', 1)[1].lower()
unique_name = f"{uuid.uuid4().hex}.{ext}"
return unique_name
@app.route('/login', methods=['GET', 'POST'])
def login():
form = LoginForm()
if form.validate_on_submit():
admin = AdminUser.query.filter_by(username=form.username.data).first()
if admin and admin.check_password(form.password.data):
login_user(admin)
flash('تم تسجيل الدخول بنجاح.', 'success')
return redirect(url_for('dashboard'))
else:
flash('اسم المستخدم أو كلمة المرور غير صحيحة.', 'danger')
return render_template('login.html', form=form)
@app.route('/logout')
@login_required
def logout():
logout_user()
flash('تم تسجيل الخروج بنجاح.', 'info')
return redirect(url_for('login'))
@app.route('/')
@login_required
def dashboard():
total_bots = CreatedBot.query.count()
total_users = UserInfo.query.count()
return render_template('dashboard.html', total_bots=total_bots, total_users=total_users)
@app.route('/upload_bot', methods=['GET', 'POST'])
@login_required
def upload_bot():
form = UploadBotForm()
users = UserInfo.query.all()
form.user.choices = [(0, "غير معين")] + [(user.user_id, user.username) for user in users]
if form.validate_on_submit():
bot_file = form.bot_file.data
info_file = form.info_file.data
if bot_file and allowed_file(bot_file.filename):
bot_filename = secure_filename(bot_file.filename)
unique_bot_filename = generate_unique_filename(bot_filename)
else:
flash('نوع ملف البوت غير مسموح به. يرجى رفع ملف Python (.py).', 'danger')
return redirect(request.url)
if info_file and allowed_file(info_file.filename):
info_filename = secure_filename(info_file.filename)
unique_info_filename = generate_unique_filename(info_filename)
else:
flash('نوع ملف المعلومات غير مسموح به. يرجى رفع ملف JSON (.json).', 'danger')
return redirect(request.url)
bot_path = os.path.join(app.config['UPLOAD_FOLDER'], form.name.data)
os.makedirs(bot_path, exist_ok=True)
if bot_file:
bot_file.save(os.path.join(bot_path, unique_bot_filename))
if info_file:
info_file.save(os.path.join(bot_path, unique_info_filename))
info_file_path = os.path.join(bot_path, unique_info_filename) if info_file else os.path.join(bot_path, "info.json")
if not os.path.exists(info_file_path):
info = {
"name": form.name.data,
"version": form.version.data,
"description": form.description.data,
"entry_point": form.entry_point.data,
"premium_only": form.premium_only.data
}
try:
with open(info_file_path, 'w', encoding='utf-8') as f:
json.dump(info, f, ensure_ascii=False, indent=4)
except Exception as e:
flash(f'حدث خطأ أثناء إنشاء ملف المعلومات: {e}', 'danger')
return redirect(request.url)
else:
try:
with open(info_file_path, 'r', encoding='utf-8') as f:
data = json.load(f)
except json.JSONDecodeError:
flash('ملف المعلومات المرفوع غير صالح (JSON غير صحيح).', 'danger')
return redirect(request.url)
user_id = form.user.data if form.user.data != 0 else None
try:
bot_record = CreatedBot(
user_id=user_id,
folder_name=bot_path,
pid=None,
service_name=None,
status='stopped'
)
db.session.add(bot_record)
db.session.commit()
flash('تم رفع البوت بنجاح.', 'success')
return redirect(url_for('dashboard'))
except Exception as e:
flash(f'حدث خطأ أثناء إضافة البوت إلى قاعدة البيانات: {e}', 'danger')
return redirect(request.url)
return render_template('upload_bot.html', form=form)
@app.route('/ads', methods=['GET', 'POST'])
@login_required
def manage_ads():
form = AddAdForm()
if form.validate_on_submit():
try:
ad = Ad(
content=form.ad_content.data,
active=form.active.data
)
db.session.add(ad)
db.session.commit()
flash('تم إضافة/تعديل الإعلان بنجاح.', 'success')
return redirect(url_for('manage_ads'))
except Exception as e:
flash(f'حدث خطأ أثناء إضافة الإعلان: {e}', 'danger')
return redirect(request.url)
ads = Ad.query.all()
return render_template('manage_ads.html', form=form, ads=ads)
@app.route('/bots')
@login_required
def bots():
bots = CreatedBot.query.all()
return render_template('bots.html', bots=bots)
@app.route('/users')
@login_required
def users():
users = UserInfo.query.all()
return render_template('users.html', users=users)
@app.route('/manage_bot/<int:bot_id>/<action>')
@login_required
def manage_bot(bot_id, action):
bot = CreatedBot.query.get(bot_id)
if not bot:
flash('البوت غير موجود.', 'danger')
return redirect(url_for('bots'))
if action == 'start':
try:
info_path = os.path.join(bot.folder_name, 'info.json')
if not os.path.exists(info_path):
flash('ملف المعلومات (info.json) غير موجود.', 'danger')
return redirect(url_for('bots'))
with open(info_path, 'r', encoding='utf-8') as f:
info = json.load(f)
entry_point = info.get('entry_point', 'bot.py')
bot_file_path = os.path.join(bot.folder_name, entry_point)
if not os.path.exists(bot_file_path):
flash(f'ملف البوت "{entry_point}" غير موجود.', 'danger')
return redirect(url_for('bots'))
process = subprocess.Popen(["python3", entry_point], cwd=bot.folder_name)
bot.pid = process.pid
bot.status = 'running'
db.session.commit()
flash('تم تشغيل البوت بنجاح.', 'success')
except Exception as e:
flash(f'حدث خطأ أثناء تشغيل البوت: {e}', 'danger')
elif action == 'stop':
if bot.pid:
try:
os.kill(bot.pid, 9)
bot.status = 'stopped'
bot.pid = None
db.session.commit()
flash('تم إيقاف البوت بنجاح.', 'success')
except Exception as e:
flash(f'حدث خطأ أثناء إيقاف البوت: {e}', 'danger')
else:
flash('لا يوجد PID للبوت.', 'warning')
else:
flash('إجراء غير معروف.', 'danger')
return redirect(url_for('bots'))
@app.errorhandler(413)
def request_entity_too_large(error):
flash('الملف المرفوع كبير جدًا. الحد الأقصى لحجم الملف هو 16 ميجابايت.', 'danger')
return redirect(request.url), 413
@app.errorhandler(404)
def not_found_error(error):
return render_template('404.html'), 404
@app.errorhandler(500)
def internal_error(error):
db.session.rollback()
return render_template('500.html'), 500
if __name__ == '__main__':
app.run(host='0.0.0.0', port=5000, debug=False)