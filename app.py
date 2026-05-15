"""NutriEase — Flask application entry point.

Author: Shivam Kumar <codexshivam@gmail.com>
"""
import os, io, json, random, string
from datetime import datetime, timedelta
from functools import wraps

from flask import (Flask, render_template, request, redirect, url_for, flash,
                   send_file, jsonify, abort)
from flask_login import (LoginManager, login_user, logout_user, login_required,
                         current_user)
from werkzeug.security import generate_password_hash, check_password_hash

from models import (db, User, Profile, DietPlan, DeficiencyReport,
                    Conversation, Message, WeightLog, Reminder, PasswordResetOTP, DoctorQuery)
from diet_planner import generate_plan
from deficiency import analyze
import chatbot
from pdf_export import diet_plan_pdf

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, "data", "nutriease.sqlite")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("NUTRIEASE_SECRET", "change-me-in-production")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = "auth"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


def admin_required(fn):
    @wraps(fn)
    def wrapper(*a, **kw):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return fn(*a, **kw)
    return wrapper


with app.app_context():
    db.create_all()
    # Bootstrap an admin user if none exists.
    if not User.query.filter_by(is_admin=True).first():
        admin_email = os.environ.get("NUTRIEASE_ADMIN_EMAIL", "admin@nutriease.local")
        admin_pw = os.environ.get("NUTRIEASE_ADMIN_PASSWORD", "admin1234")
        if not User.query.filter_by(email=admin_email).first():
            db.session.add(User(
                email=admin_email,
                full_name="NutriEase Admin",
                password_hash=generate_password_hash(admin_pw),
                is_admin=True,
            ))
            db.session.commit()
            print(f"[NutriEase] Admin bootstrap: {admin_email} / {admin_pw}")


# ---------------- Public pages ----------------

@app.route("/")
def landing():
    return render_template("landing.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/services")
def services():
    return render_template("services.html")

@app.route("/privacy")
def privacy():
    return render_template("privacy.html")

@app.route("/terms")
def terms():
    return render_template("terms.html")


# ---------------- Auth ----------------

@app.route("/auth", methods=["GET", "POST"])
def auth():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        action = request.form.get("action")
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if action == "signin":
            user = User.query.filter_by(email=email).first()
            if not user or not check_password_hash(user.password_hash, password):
                flash("Invalid email or password.", "error")
                return redirect(url_for("auth"))
            user.last_login = datetime.utcnow()
            db.session.commit()
            login_user(user)
            return redirect(url_for("admin_panel" if user.is_admin else "dashboard"))

        if action == "signup":
            if User.query.filter_by(email=email).first():
                flash("An account with that email already exists.", "error")
                return redirect(url_for("auth"))
            if len(password) < 6:
                flash("Password must be at least 6 characters.", "error")
                return redirect(url_for("auth"))
            user = User(email=email,
                        password_hash=generate_password_hash(password),
                        full_name=request.form.get("full_name", ""))
            db.session.add(user)
            db.session.flush()
            profile = Profile(
                user_id=user.id,
                age=int(request.form["age"]) if request.form.get("age") else None,
                gender=request.form.get("gender", "male"),
                height_cm=float(request.form["height_cm"]) if request.form.get("height_cm") else None,
                weight_kg=float(request.form["weight_kg"]) if request.form.get("weight_kg") else None,
            )
            db.session.add(profile)
            db.session.commit()
            login_user(user)
            flash("Welcome to NutriEase!", "success")
            return redirect(url_for("dashboard"))

    return render_template("auth.html")


@app.route("/forgot", methods=["GET", "POST"])
def forgot():
    """Request an OTP. We log it to the server console (demo email transport)."""
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        user = User.query.filter_by(email=email).first()
        if user:
            code = "".join(random.choices(string.digits, k=6))
            otp = PasswordResetOTP(email=email, code=code,
                                   expires_at=datetime.utcnow() + timedelta(minutes=15))
            db.session.add(otp)
            db.session.commit()
            print(f"[NutriEase] Password reset OTP for {email}: {code}")
        flash("If that email exists, an OTP has been sent. Check your inbox (or server console in demo mode).", "success")
        return redirect(url_for("reset", email=email))
    return render_template("forgot.html")


@app.route("/reset", methods=["GET", "POST"])
def reset():
    email = request.values.get("email", "").strip().lower()
    if request.method == "POST":
        code = request.form.get("code", "").strip()
        new_pw = request.form.get("password", "")
        if len(new_pw) < 6:
            flash("Password must be at least 6 characters.", "error")
            return redirect(url_for("reset", email=email))
        otp = (PasswordResetOTP.query
               .filter_by(email=email, code=code, used=False)
               .order_by(PasswordResetOTP.created_at.desc()).first())
        if not otp or otp.expires_at < datetime.utcnow():
            flash("Invalid or expired OTP.", "error")
            return redirect(url_for("reset", email=email))
        user = User.query.filter_by(email=email).first()
        if not user:
            flash("Account not found.", "error")
            return redirect(url_for("forgot"))
        user.password_hash = generate_password_hash(new_pw)
        otp.used = True
        db.session.commit()
        flash("Password updated. Please sign in.", "success")
        return redirect(url_for("auth"))
    return render_template("reset.html", email=email)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("landing"))


# ---------------- App pages ----------------

@app.route("/app")
@login_required
def dashboard():
    plans = DietPlan.query.filter_by(user_id=current_user.id).order_by(DietPlan.created_at.desc()).limit(3).all()
    weights = WeightLog.query.filter_by(user_id=current_user.id).order_by(WeightLog.logged_at.desc()).limit(10).all()
    reminders = Reminder.query.filter_by(user_id=current_user.id, enabled=True).all()

    p = current_user.profile
    summary = None
    if p and p.height_cm and p.weight_kg and p.age:
        b = chatbot.bmi(p.weight_kg, p.height_cm)
        summary = {
            "bmi": b,
            "category": chatbot.bmi_category(b),
            "calories": chatbot.daily_calories({
                "weight_kg": p.weight_kg, "height_cm": p.height_cm,
                "age": p.age, "gender": p.gender or "male",
                "activity_level": p.activity_level or "moderate",
                "goal": p.goal or "maintain",
            }),
        }
    return render_template("dashboard.html", plans=plans, weights=weights,
                           reminders=reminders, summary=summary)


@app.route("/app/weight", methods=["POST"])
@login_required
def log_weight():
    w = request.form.get("weight_kg", type=float)
    if w and 20 <= w <= 400:
        db.session.add(WeightLog(user_id=current_user.id, weight_kg=w,
                                 note=request.form.get("note", "")[:200]))
        if current_user.profile:
            current_user.profile.weight_kg = w
        db.session.commit()
        flash("Weight logged.", "success")
    return redirect(url_for("dashboard"))


@app.route("/app/reminder/add", methods=["POST"])
@login_required
def add_reminder():
    db.session.add(Reminder(
        user_id=current_user.id,
        kind=request.form.get("kind", "meal"),
        title=request.form.get("title", "Reminder")[:200],
        time_of_day=request.form.get("time_of_day", "08:00"),
    ))
    db.session.commit()
    flash("Reminder added.", "success")
    return redirect(url_for("dashboard"))


@app.route("/app/reminder/<int:rid>/delete", methods=["POST"])
@login_required
def delete_reminder(rid):
    r = Reminder.query.filter_by(id=rid, user_id=current_user.id).first_or_404()
    db.session.delete(r)
    db.session.commit()
    return redirect(url_for("dashboard"))


@app.route("/app/profile", methods=["GET", "POST"])
@login_required
def profile():
    p = current_user.profile or Profile(user_id=current_user.id)
    if request.method == "POST":
        current_user.full_name = request.form.get("full_name", current_user.full_name)
        for fld in ["gender", "activity_level", "goal", "diet_preference",
                    "allergies", "deficiencies", "medical_conditions"]:
            setattr(p, fld, request.form.get(fld) or getattr(p, fld))
        for fld in ["age"]:
            v = request.form.get(fld)
            if v: setattr(p, fld, int(v))
        for fld in ["height_cm", "weight_kg"]:
            v = request.form.get(fld)
            if v: setattr(p, fld, float(v))
        if not p.id:
            db.session.add(p)
        db.session.commit()
        flash("Profile saved.", "success")
        return redirect(url_for("profile"))
    return render_template("profile.html", p=p)


@app.route("/app/plan", methods=["GET", "POST"])
@login_required
def plan_page():
    plan = None
    plan_id = None
    if request.method == "POST":
        form = {k: v for k, v in request.form.items()}
        
        # Save profile
        p = current_user.profile or Profile(user_id=current_user.id)
        for fld in ["gender", "activity_level", "goal", "diet_preference", "allergies", "deficiencies", "medical_conditions"]:
            setattr(p, fld, form.get(fld) or getattr(p, fld))
        for fld in ["age"]:
            v = form.get(fld)
            if v: setattr(p, fld, int(v))
        for fld in ["height_cm", "weight_kg"]:
            v = form.get(fld)
            if v: setattr(p, fld, float(v))
        if not p.id:
            db.session.add(p)
            
        plan = generate_plan(form)
        rec = DietPlan(user_id=current_user.id, title=plan["title"], goal=form.get("goal"),
                       calories=plan["daily_calories"], plan_json=json.dumps(plan))
        db.session.add(rec)
        db.session.commit()
        plan_id = rec.id
    return render_template("plan.html", plan=plan, plan_id=plan_id, profile=current_user.profile)


@app.route("/app/plan/<int:plan_id>/pdf")
@login_required
def plan_pdf(plan_id):
    rec = DietPlan.query.filter_by(id=plan_id, user_id=current_user.id).first_or_404()
    pdf_bytes = diet_plan_pdf(json.loads(rec.plan_json), user_name=current_user.full_name or "")
    return send_file(io.BytesIO(pdf_bytes), mimetype="application/pdf",
                     as_attachment=True, download_name=f"NutriEase_Plan_{rec.id}.pdf")


@app.route("/app/deficiency", methods=["GET", "POST"])
@login_required
def deficiency():
    report = None
    if request.method == "POST":
        symptoms = request.form.get("symptoms", "")
        report = analyze(symptoms)
        rec = DeficiencyReport(user_id=current_user.id, symptoms=symptoms,
                               report_json=json.dumps(report))
        db.session.add(rec)
        db.session.commit()
    return render_template("deficiency.html", report=report)


# ---------------- Conversational chatbot ----------------

@app.route("/chat", methods=["GET", "POST"])
def chat():
    """Chat is available to everyone but only persists for logged-in users."""
    conv = None
    convs = []
    if current_user.is_authenticated:
        conv_id = request.args.get("conv", type=int)
        if conv_id:
            conv = Conversation.query.filter_by(id=conv_id, user_id=current_user.id).first_or_404()
        convs = (Conversation.query.filter_by(user_id=current_user.id)
                 .order_by(Conversation.created_at.desc()).all())

    if request.method == "POST":
        if not current_user.is_authenticated:
            flash("Please sign in to start a chat.", "error")
            return redirect(url_for("auth"))

        text = request.form.get("message", "").strip()
        if not text:
            return redirect(url_for("chat", conv=conv.id if conv else None))

        if conv is None:
            conv = Conversation(user_id=current_user.id, title=text[:60])
            db.session.add(conv)
            db.session.flush()
            # Fresh conversations begin with onboarding so the coach can profile the user.
            opener = chatbot.start_onboarding(conv)
            db.session.add(Message(conversation_id=conv.id, role="assistant", content=opener))

        db.session.add(Message(conversation_id=conv.id, role="user", content=text))

        prof = current_user.profile
        prof_d = {"goal": getattr(prof, "goal", None),
                  "diet_preference": getattr(prof, "diet_preference", None)} if prof else None

        reply, finished = chatbot.reply(conv, text, profile=prof_d)

        if finished and prof:
            # Persist any onboarding answers to the user profile.
            for k in ("age", "gender", "height_cm", "weight_kg", "activity_level",
                      "goal", "diet_preference", "medical_conditions"):
                if k in finished and finished[k] not in (None, ""):
                    setattr(prof, k, finished[k])
            if finished.get("name") and not current_user.full_name:
                current_user.full_name = finished["name"]

        db.session.add(Message(conversation_id=conv.id, role="assistant", content=reply))
        db.session.commit()
        return redirect(url_for("chat", conv=conv.id))

    return render_template("chat.html", conv=conv, convs=convs)


@app.route("/chat/new")
@login_required
def chat_new():
    conv = Conversation(user_id=current_user.id, title="New consultation")
    db.session.add(conv)
    db.session.flush()
    opener = chatbot.start_onboarding(conv)
    db.session.add(Message(conversation_id=conv.id, role="assistant", content=opener))
    db.session.commit()
    return redirect(url_for("chat", conv=conv.id))


@app.route("/app/history")
@login_required
def history():
    plans = DietPlan.query.filter_by(user_id=current_user.id).order_by(DietPlan.created_at.desc()).all()
    reports = DeficiencyReport.query.filter_by(user_id=current_user.id).order_by(DeficiencyReport.created_at.desc()).all()
    convs = Conversation.query.filter_by(user_id=current_user.id).order_by(Conversation.created_at.desc()).all()
    return render_template("history.html", plans=plans, reports=reports, convs=convs)


# ---------------- Public REST API ----------------

@app.route("/api/chat", methods=["POST"])
def api_chat():
    """Lightweight stateless API for embedding the chatbot."""
    payload = request.get_json(silent=True) or {}
    q = (payload.get("message") or "").strip()
    if not q:
        return jsonify({"error": "missing 'message'"}), 400
    return jsonify({"reply": chatbot.free_answer(q, profile=payload.get("profile"))})


@app.route("/api/bmi", methods=["POST"])
def api_bmi():
    p = request.get_json(silent=True) or {}
    try:
        w = float(p["weight_kg"]); h = float(p["height_cm"])
    except (KeyError, ValueError, TypeError):
        return jsonify({"error": "weight_kg and height_cm required"}), 400
    b = chatbot.bmi(w, h)
    return jsonify({"bmi": b, "category": chatbot.bmi_category(b)})


# ---------------- Admin ----------------

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if current_user.is_authenticated:
        if current_user.is_admin: return redirect(url_for("admin_panel"))
        if current_user.is_doctor: return redirect(url_for("doctor_portal"))
        
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        pwd = request.form.get("password", "")
        
        # Fallback master admin check for emergencies
        if email == "admin@nutrease.com" and pwd == "admin123":
            # Check if this master user exists, if not create it
            master = User.query.filter_by(email="admin@nutrease.com").first()
            if not master:
                master = User(email="admin@nutrease.com", password_hash=generate_password_hash("admin123"), is_admin=True)
                db.session.add(master)
                db.session.commit()
            master.is_admin = True
            db.session.commit()
            login_user(master)
            flash("Master Admin access granted.", "success")
            return redirect(url_for("admin_panel"))
            
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, pwd):
            if user.is_admin:
                login_user(user)
                flash("Admin logged in.", "success")
                return redirect(url_for("admin_panel"))
            elif user.is_doctor:
                login_user(user)
                flash("Dietitian logged in.", "success")
                return redirect(url_for("doctor_portal"))
            else:
                flash("Access denied. You do not have staff privileges.", "error")
        else:
            flash("Invalid email or password.", "error")
            
    return render_template("admin_login.html")


@app.route("/admin")
@login_required
@admin_required
def admin_panel():
    stats = {
        "users": User.query.count(),
        "plans": DietPlan.query.count(),
        "conversations": Conversation.query.count(),
        "messages": Message.query.count(),
    }
    users = User.query.order_by(User.created_at.desc()).limit(50).all()
    return render_template("admin.html", stats=stats, users=users)

@app.route("/admin/create_doctor", methods=["POST"])
@login_required
@admin_required
def admin_create_doctor():
    name = request.form.get("name")
    email = request.form.get("email").lower().strip()
    pwd = request.form.get("password")
    
    if User.query.filter_by(email=email).first():
        flash("Email already registered.", "error")
        return redirect(url_for("admin_panel"))
        
    u = User(email=email, password_hash=generate_password_hash(pwd), full_name=name, is_doctor=True)
    db.session.add(u)
    db.session.commit()
    flash("Dietitian account created successfully.", "success")
    return redirect(url_for("admin_panel"))


@app.route("/admin/user/<int:uid>/toggle-admin", methods=["POST"])
@login_required
@admin_required
def admin_toggle(uid):
    u = User.query.get_or_404(uid)
    if u.id != current_user.id:
        u.is_admin = not u.is_admin
        db.session.commit()
    return redirect(url_for("admin_panel"))


@app.route("/admin/user/<int:uid>/delete", methods=["POST"])
@login_required
@admin_required
def admin_delete(uid):
    u = User.query.get_or_404(uid)
    if u.id != current_user.id:
        db.session.delete(u)
        db.session.commit()
    return redirect(url_for("admin_panel"))
@app.route("/admin/user/<int:uid>/toggle-doctor", methods=["POST"])
@login_required
@admin_required
def admin_toggle_doctor(uid):
    u = User.query.get_or_404(uid)
    u.is_doctor = not u.is_doctor
    db.session.commit()
    return redirect(url_for("admin_panel"))


@app.route("/ask_doctor", methods=["GET", "POST"])
@login_required
def ask_doctor():
    if request.method == "POST":
        msg = request.form.get("message", "").strip()
        if msg:
            query = DoctorQuery(user_id=current_user.id, message=msg)
            db.session.add(query)
            db.session.commit()
            flash("Your message has been sent to our doctors.", "success")
        return redirect(url_for("ask_doctor"))
    
    queries = DoctorQuery.query.filter_by(user_id=current_user.id).order_by(DoctorQuery.created_at.desc()).all()
    return render_template("ask_doctor.html", queries=queries)


@app.route("/doctor_portal", methods=["GET", "POST"])
@login_required
def doctor_portal():
    if not getattr(current_user, 'is_doctor', False):
        abort(403)
        
    if request.method == "POST":
        qid = request.form.get("query_id", type=int)
        reply = request.form.get("reply", "").strip()
        q = DoctorQuery.query.get_or_404(qid)
        if reply and q.status == "pending":
            q.reply = reply
            q.status = "answered"
            q.doctor_id = current_user.id
            q.replied_at = datetime.utcnow()
            db.session.commit()
            flash("Reply sent.", "success")
        return redirect(url_for("doctor_portal"))
        
    pending = DoctorQuery.query.filter_by(status="pending").order_by(DoctorQuery.created_at.asc()).all()
    answered = DoctorQuery.query.filter_by(status="answered", doctor_id=current_user.id).order_by(DoctorQuery.replied_at.desc()).limit(20).all()
    return render_template("doctor_portal.html", pending=pending, answered=answered)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
