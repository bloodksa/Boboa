from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user
from database import AdminUser
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length
auth = Blueprint('auth', __name__)
class LoginForm(FlaskForm):
username = StringField('اسم المستخدم', validators=[DataRequired(), Length(min=4, max=150)])
password = PasswordField('كلمة المرور', validators=[DataRequired(), Length(min=4, max=150)])
submit = SubmitField('تسجيل الدخول')
@auth.route('/login', methods=['GET', 'POST'])
def login():
form = LoginForm()
if form.validate_on_submit():
username = form.username.data
password = form.password.data
admin = AdminUser.query.filter_by(username=username).first()
if admin and admin.check_password(password):
login_user(admin)
flash("تم تسجيل الدخول بنجاح", "success")
return redirect(url_for('index'))
flash("اسم المستخدم أو كلمة المرور غير صحيحة", "danger")
return render_template("login.html", form=form)
@auth.route('/logout')
def logout():
logout_user()
flash("تم تسجيل الخروج بنجاح", "info")
return redirect(url_for('auth.login'))