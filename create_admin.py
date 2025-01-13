from database import db, AdminUser
from flask import current_app
from web_admin import app
def create_admin_user(username, password):
existing_admin = AdminUser.query.filter_by(username=username).first()
if existing_admin:
print("المشرف بهذا الاسم موجود بالفعل.")
return
admin = AdminUser(username=username)
admin.set_password(password)
db.session.add(admin)
db.session.commit()
print(f"تم إنشاء المشرف '{username}' بنجاح.")
if __name__ == '__main__':
with app.app_context():
username = input("أدخل اسم المستخدم للمشرف الجديد: ")
password = input("أدخل كلمة المرور للمشرف الجديد: ")
create_admin_user(username, password)