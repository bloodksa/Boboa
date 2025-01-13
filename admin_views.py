from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask import redirect, url_for, flash
from flask_login import current_user
class MyAdminIndexView(AdminIndexView):
def is_accessible(self):
return current_user.is_authenticated and getattr(current_user, 'is_admin', False)
def inaccessible_callback(self, name, **kwargs):
flash("الدخول مقيّد للمشرفين", "danger")
return redirect(url_for('login'))
class MyModelView(ModelView):
def is_accessible(self):
return current_user.is_authenticated and getattr(current_user, 'is_admin', False)
def inaccessible_callback(self, name, **kwargs):
flash("الدخول مقيّد للمشرفين", "danger")
return redirect(url_for('login'))
def setup_admin(app):
admin = Admin(app, name="لوحة التحكم", template_mode="bootstrap3", index_view=MyAdminIndexView())
from database import AdminUser, UserInfo, CreatedBot, SupportTicket, SupportMessage, Ad
session = app.extensions["sqlalchemy"].db.session
admin.add_view(MyModelView(AdminUser, session))
admin.add_view(MyModelView(UserInfo, session))
admin.add_view(MyModelView(CreatedBot, session))
admin.add_view(MyModelView(SupportTicket, session))
admin.add_view(MyModelView(SupportMessage, session))
admin.add_view(MyModelView(Ad, session))