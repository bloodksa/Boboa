import os
from pathlib import Path
import datetime
from sqlalchemy import (
create_engine, Column, Integer, String, Boolean,
DateTime, ForeignKey, Text
)
from sqlalchemy.orm import (
declarative_base, sessionmaker, relationship
)
DB_DIR = Path("data")
DB_DIR.mkdir(exist_ok=True)
DB_PATH = DB_DIR / "mother_bot.db"
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
Base = declarative_base()

from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
SessionLocal = sessionmaker(bind=engine)
class UserState(Base):
"""
حالة المستخدم بالنسبة للبوت الأم:
- chat_id: معرف فريد (الدردشة)
- stage: المرحلة الحالية (مثلاً: choose_template، waiting_for_token، ...)
- template_chosen: اسم القالب المختار
"""
__tablename__ = "user_states"
chat_id = Column(String, primary_key=True)
stage = Column(String, default="")
template_chosen = Column(String, default="")
class UserInfo(Base):
    last_login = Column(DateTime, nullable=True)
    profile_picture = Column(String, default='default.jpg')
"""
معلومات المستخدم الأساسية:
- user_id: الرقم التعريفي للمستخدم في تيليجرام
- username: اسم المستخدم
- is_admin: حالة المدير
- is_banned: حالة الحظر
- has_paid: حالة الدفع (إن وُجد نظام دفع)
- created_bots: عدد البوتات المُنشأة
- max_bots: الحد الأقصى للبوتات المسموح بها
- language: لغة الواجهة (مثلاً "ar" أو "en")
- premium_until: تاريخ انتهاء الاشتراك المميز (إن وُجد)
"""
__tablename__ = "user_info"
user_id = Column(Integer, primary_key=True, index=True)
username = Column(String, default="")
is_admin = Column(Boolean, default=False)
is_banned = Column(Boolean, default=False)
has_paid = Column(Boolean, default=False)
created_bots = Column(Integer, default=0)
max_bots = Column(Integer, default=3)
language = Column(String, default="ar")
premium_until = Column(DateTime, nullable=True)
bots = relationship("CreatedBot", backref="owner", lazy=True)
support_tickets = relationship("SupportTicket", backref="user", lazy=True)
class CreatedBot(Base):
"""
بوتات المستخدم:
- id: تسلسل فريد
- user_id: معرف المستخدم (مرتبط بجدول user_info)
- folder_name: مسار المجلد الذي يحوي ملفات البوت
- pid: رقم العملية (إن تم تشغيل البوت)
- service_name: اسم الخدمة (إذا تم استخدام systemd)
- status: حالة تشغيل البوت (مثلاً running أو stopped)
- created_at: وقت إنشاء السجل
"""
__tablename__ = "created_bots"
id = Column(Integer, primary_key=True, index=True)
user_id = Column(Integer, ForeignKey("user_info.user_id"), nullable=True)
folder_name = Column(String, default="")
pid = Column(Integer, nullable=True)
service_name = Column(String, nullable=True)
status = Column(String, default="stopped")
created_at = Column(DateTime, default=datetime.datetime.utcnow)
class SupportTicket(Base):
"""
تذاكر الدعم:
- id: رقم التذكرة
- user_id: معرف المستخدم (مرتبط بجدول user_info)
- title: عنوان التذكرة
- status: (open أو closed)
- created_at: وقت الإنشاء
- messages: قائمة الرسائل المرتبطة
"""
__tablename__ = "support_tickets"
id = Column(Integer, primary_key=True, index=True)
user_id = Column(Integer, ForeignKey("user_info.user_id"))
title = Column(String, default="")
status = Column(String, default="open")
created_at = Column(DateTime, default=datetime.datetime.utcnow)
messages = relationship("SupportMessage", back_populates="ticket", cascade="all, delete, delete-orphan")
class SupportMessage(Base):
"""
رسائل الدعم:
- id: تسلسل فريد
- ticket_id: معرف التذكرة (مرتبط بجدول support_tickets)
- sender_id: معرف المرسل (مستخدم أو مشرف)
- text: نص الرسالة
- created_at: وقت الإنشاء
"""
__tablename__ = "support_messages"
id = Column(Integer, primary_key=True, index=True)
ticket_id = Column(Integer, ForeignKey("support_tickets.id"))
sender_id = Column(Integer)
text = Column(Text)
created_at = Column(DateTime, default=datetime.datetime.utcnow)
ticket = relationship("SupportTicket", back_populates="messages")
class AdminUser(Base):

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
        """
حسابات المشرفين:
- id: تسلسل فريد
- username: اسم المستخدم (فريد)
- password_hash: كلمة المرور المشفرة
- created_at: تاريخ الإنشاء
"""
__tablename__ = "admin_users"
id = Column(Integer, primary_key=True, index=True)
username = Column(String, unique=True, nullable=False)
password_hash = Column(String, nullable=False)
created_at = Column(DateTime, default=datetime.datetime.utcnow)
def set_password(self, password):
self.password_hash = generate_password_hash(password)
def check_password(self, password):
return check_password_hash(self.password_hash, password)
class Ad(Base):
"""
الإعلانات:
- id: تسلسل فريد
- content: محتوى الإعلان
- active: حالة الإعلان (نشط/غير نشط)
- created_at: وقت الإنشاء
"""
__tablename__ = "ads"
id = Column(Integer, primary_key=True, index=True)
content = Column(String, nullable=False)
active = Column(Boolean, default=True)
created_at = Column(DateTime, default=datetime.datetime.utcnow)
def initialize_admin():
"""
إنشاء مشرف أولي إذا لم يكن موجودًا.
إذا كان جدول admin_users فارغًا، سيتم طلب إدخال اسم المستخدم وكلمة المرور للمشرف الأول.
"""
existing_admin = AdminUser.query.first()
if not existing_admin:
print("لا يوجد مشرفين حاليًا. سيتم إنشاء مشرف أولي.")
username = input("أدخل اسم المستخدم للمشرف الأول: ")
password = input("أدخل كلمة المرور للمشرف الأول: ")
try:
admin = AdminUser(username=username)
admin.set_password(password)
db.session.add(admin)
db.session.commit()
print(f"تم إنشاء المشرف '{username}' بنجاح.")
except Exception as e:
print(f"حدث خطأ أثناء إنشاء المشرف: {e}")
else:
print("يوجد مشرفين بالفعل.")
def get_session():
"""ترجع جلسة عمل جديدة"""
return SessionLocal()
def get_user_state(chat_id: str) -> UserState:
"""
الحصول على حالة المستخدم.
إذا لم تكن موجودة، يتم إنشاؤها.
"""
s = get_session()
st = s.query(UserState).filter_by(chat_id=chat_id).first()
if not st:
st = UserState(chat_id=chat_id)
s.add(st)
s.commit()
s.close()
return st
def set_user_stage(chat_id: str, stage: str):
s = get_session()
st = s.query(UserState).filter_by(chat_id=chat_id).first()
if not st:
st = UserState(chat_id=chat_id, stage=stage)
s.add(st)
else:
st.stage = stage
s.commit()
s.close()
def set_user_template(chat_id: str, template: str):
s = get_session()
st = s.query(UserState).filter_by(chat_id=chat_id).first()
if not st:
st = UserState(chat_id=chat_id, stage="waiting_for_token", template_chosen=template)
s.add(st)
else:
st.template_chosen = template
s.commit()
s.close()
def clear_user_state(chat_id: str):
s = get_session()
st = s.query(UserState).filter_by(chat_id=chat_id).first()
if st:
s.delete(st)
s.commit()
s.close()
def get_or_create_userinfo(user_id: int) -> UserInfo:
s = get_session()
u = s.query(UserInfo).filter_by(user_id=user_id).first()
if not u:
u = UserInfo(user_id=user_id)
s.add(u)
s.commit()
s.close()
return u
def is_user_banned(user_id: int) -> bool:
s = get_session()
u = s.query(UserInfo).filter_by(user_id=user_id).first()
result = u.is_banned if u else False
s.close()
return result
def is_user_admin(user_id: int) -> bool:
s = get_session()
u = s.query(UserInfo).filter_by(user_id=user_id).first()
result = u.is_admin if u else False
s.close()
return result
def has_user_paid(user_id: int) -> bool:
s = get_session()
u = s.query(UserInfo).filter_by(user_id=user_id).first()
result = u.has_paid if u else False
s.close()
return result
def increment_created_bots(user_id: int):
s = get_session()
u = s.query(UserInfo).filter_by(user_id=user_id).first()
if u:
u.created_bots += 1
s.commit()
s.close()
def set_max_bots(user_id: int, num: int):
s = get_session()
u = s.query(UserInfo).filter_by(user_id=user_id).first()
if u:
u.max_bots = num
s.commit()
s.close()
def set_user_paid(user_id: int, paid=True):
s = get_session()
u = s.query(UserInfo).filter_by(user_id=user_id).first()
if u:
u.has_paid = paid
s.commit()
s.close()
def ban_user(user_id: int):
s = get_session()
u = s.query(UserInfo).filter_by(user_id=user_id).first()
if u:
u.is_banned = True
s.commit()
s.close()
def unban_user(user_id: int):
s = get_session()
u = s.query(UserInfo).filter_by(user_id=user_id).first()
if u:
u.is_banned = False
s.commit()
s.close()
def add_created_bot(user_id: int, folder_name: str, pid=None, service_name=None, status="running") -> int:
s = get_session()
cb = CreatedBot(
user_id=user_id,
folder_name=folder_name,
pid=pid,
service_name=service_name,
status=status
)
s.add(cb)
s.commit()
bot_id = cb.id
s.close()
return bot_id
def update_bot_status(bot_id: int, status: str):
s = get_session()
cb = s.query(CreatedBot).filter_by(id=bot_id).first()
if cb:
cb.status = status
s.commit()
s.close()
def get_user_bots(user_id: int):
s = get_session()
bots = s.query(CreatedBot).filter_by(user_id=user_id).all()
s.close()
return bots
def get_all_bots():
s = get_session()
bots = s.query(CreatedBot).all()
s.close()
return bots
def create_support_ticket(user_id: int, title: str) -> int:
s = get_session()
ticket = SupportTicket(
user_id=user_id,
title=title,
status="open"
)
s.add(ticket)
s.commit()
tid = ticket.id
s.close()
return tid
def add_support_message(ticket_id: int, sender_id: int, text: str):
s = get_session()
msg = SupportMessage(
ticket_id=ticket_id,
sender_id=sender_id,
text=text
)
s.add(msg)
s.commit()
s.close()
def close_ticket(ticket_id: int):
s = get_session()
ticket = s.query(SupportTicket).filter_by(id=ticket_id).first()
if ticket and ticket.status != "closed":
ticket.status = "closed"
s.commit()
s.close()
def get_user_tickets(user_id: int):
s = get_session()
tickets = s.query(SupportTicket).filter_by(user_id=user_id).all()
s.close()
return tickets
def get_ticket_messages(ticket_id: int):
"""
يعيد كل الرسائل في تذكرة ما بترتيب تصاعدي حسب وقت الإنشاء
"""
s = get_session()
msgs = s.query(SupportMessage).filter_by(ticket_id=ticket_id).order_by(SupportMessage.created_at.asc()).all()
s.close()
return msgs
Base.metadata.create_all(bind=engine)
class TicketReply(Base):
    """
    الردود على التذاكر من قبل المشرفين:
    - reply_id: الرقم التعريفي للرد
    - ticket_id: معرف التذكرة المرتبطة
    - admin_id: معرف المشرف الذي أرسل الرد
    - content: نص الرد
    - timestamp: وقت إرسال الرد
    """
    __tablename__ = "ticket_replies"
    reply_id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("support_tickets.id"), nullable=False)
    admin_id = Column(Integer, ForeignKey("admin_users.id"), nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class ActivityLog(Base):
    """
    سجل الأنشطة لتتبع جميع العمليات في النظام:
    - log_id: الرقم التعريفي للسجل
    - user_id: معرف المستخدم الذي قام بالنشاط
    - action: وصف النشاط
    - timestamp: وقت النشاط
    """
    __tablename__ = "activity_logs"
    log_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user_info.user_id"), nullable=True)
    action = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
