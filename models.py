"""NutriEase — SQLAlchemy models."""
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120))
    is_admin = db.Column(db.Boolean, default=False)
    is_doctor = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    profile = db.relationship("Profile", backref="user", uselist=False, cascade="all, delete-orphan")
    plans = db.relationship("DietPlan", backref="user", cascade="all, delete-orphan")
    reports = db.relationship("DeficiencyReport", backref="user", cascade="all, delete-orphan")
    conversations = db.relationship("Conversation", backref="user", cascade="all, delete-orphan")
    weight_logs = db.relationship("WeightLog", backref="user", cascade="all, delete-orphan")
    reminders = db.relationship("Reminder", backref="user", cascade="all, delete-orphan")
    doctor_queries_sent = db.relationship("DoctorQuery", foreign_keys="DoctorQuery.user_id", backref="user", cascade="all, delete-orphan")


class DoctorQuery(db.Model):
    __tablename__ = "doctor_queries"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"))
    doctor_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    message = db.Column(db.Text, nullable=False)
    reply = db.Column(db.Text)
    status = db.Column(db.String(20), default="pending")  # 'pending' | 'answered'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    replied_at = db.Column(db.DateTime)


class Profile(db.Model):
    __tablename__ = "profiles"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))
    height_cm = db.Column(db.Float)
    weight_kg = db.Column(db.Float)
    activity_level = db.Column(db.String(40), default="moderate")
    goal = db.Column(db.String(40), default="maintain")
    diet_preference = db.Column(db.String(40), default="non-vegetarian")
    allergies = db.Column(db.Text, default="")
    deficiencies = db.Column(db.Text, default="")
    medical_conditions = db.Column(db.Text, default="")
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DietPlan(db.Model):
    __tablename__ = "diet_plans"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"))
    title = db.Column(db.String(200))
    goal = db.Column(db.String(40))
    calories = db.Column(db.Integer)
    plan_json = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class DeficiencyReport(db.Model):
    __tablename__ = "deficiency_reports"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"))
    symptoms = db.Column(db.Text)
    report_json = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Conversation(db.Model):
    __tablename__ = "conversations"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"))
    title = db.Column(db.String(200))
    state = db.Column(db.String(40), default="free")  # 'onboarding' | 'free'
    state_data = db.Column(db.Text, default="{}")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    messages = db.relationship("Message", backref="conversation", cascade="all, delete-orphan", order_by="Message.created_at")


class Message(db.Model):
    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey("conversations.id", ondelete="CASCADE"))
    role = db.Column(db.String(20))   # 'user' | 'assistant' | 'system'
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class WeightLog(db.Model):
    __tablename__ = "weight_logs"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"))
    weight_kg = db.Column(db.Float, nullable=False)
    note = db.Column(db.String(200), default="")
    logged_at = db.Column(db.DateTime, default=datetime.utcnow)


class Reminder(db.Model):
    __tablename__ = "reminders"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"))
    kind = db.Column(db.String(40))  # 'meal' | 'workout' | 'water'
    title = db.Column(db.String(200))
    time_of_day = db.Column(db.String(10))  # 'HH:MM'
    enabled = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class PasswordResetOTP(db.Model):
    __tablename__ = "password_reset_otps"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), index=True, nullable=False)
    code = db.Column(db.String(6), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
