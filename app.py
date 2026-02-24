from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import re
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///enrollment.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ─── Database Models ───────────────────────────────────────────────────────
class User(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    full_name  = db.Column(db.String(120), nullable=False)
    email      = db.Column(db.String(120), unique=True, nullable=False)
    password   = db.Column(db.String(256), nullable=False)
    college    = db.Column(db.String(200), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    year       = db.Column(db.String(20), nullable=False)
    bio        = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    skills     = db.relationship('Skill', backref='user', lazy=True, cascade='all, delete-orphan')

class Skill(db.Model):
    id      = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name    = db.Column(db.String(100), nullable=False)
    rating  = db.Column(db.Integer, nullable=False)

# ─── Helpers ───────────────────────────────────────────────────────────────
CREATIVE_SKILLS = [
    "Graphic Design","Video Editing","Photography",
    "Music Production","UI/UX Design","Illustration",
    "Animation","Web Development","Content Writing","Public Speaking"
]

def is_valid_email(email):
    return re.match(r'^[\w\.-]+@[\w\.-]+\.\w{2,}$', email)

def password_strength(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters."
    if not re.search(r'[A-Z]', password):
        return False, "Password needs at least one uppercase letter."
    if not re.search(r'\d', password):
        return False, "Password needs at least one number."
    return True, "OK"

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in first.", "error")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

# ─── Routes ────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return redirect(url_for('dashboard') if 'user_id' in session else url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        email    = request.form.get('email','').strip().lower()
        password = request.form.get('password','')
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            flash("Invalid email or password.", "error")
            return redirect(url_for('login'))
        session['user_id']   = user.id
        session['user_name'] = user.full_name
        flash(f"Welcome back, {user.full_name}!", "success")
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        full_name  = request.form.get('full_name','').strip()
        email      = request.form.get('email','').strip().lower()
        password   = request.form.get('password','')
        confirm    = request.form.get('confirm_password','')
        college    = request.form.get('college','').strip()
        department = request.form.get('department','').strip()
        year       = request.form.get('year','').strip()
        bio        = request.form.get('bio','').strip()

        skills_data = []
        for skill in CREATIVE_SKILLS:
            rating = request.form.get(f'skill_{skill}','0')
            if rating and int(rating) > 0:
                skills_data.append({'name': skill, 'rating': int(rating)})

        if not all([full_name, email, password, confirm, college, department, year]):
            flash("Please fill in all required fields.", "error")
            return render_template('register.html', skills=CREATIVE_SKILLS, form=request.form)
        if not is_valid_email(email):
            flash("Please enter a valid email address.", "error")
            return render_template('register.html', skills=CREATIVE_SKILLS, form=request.form)
        if User.query.filter_by(email=email).first():
            flash("An account with this email already exists.", "error")
            return render_template('register.html', skills=CREATIVE_SKILLS, form=request.form)
        if password != confirm:
            flash("Passwords do not match.", "error")
            return render_template('register.html', skills=CREATIVE_SKILLS, form=request.form)
        valid, msg = password_strength(password)
        if not valid:
            flash(msg, "error")
            return render_template('register.html', skills=CREATIVE_SKILLS, form=request.form)
        if not skills_data:
            flash("Please rate at least one creative skill.", "error")
            return render_template('register.html', skills=CREATIVE_SKILLS, form=request.form)

        user = User(full_name=full_name, email=email,
                    password=generate_password_hash(password),
                    college=college, department=department, year=year, bio=bio)
        db.session.add(user)
        db.session.flush()
        for s in skills_data:
            db.session.add(Skill(user_id=user.id, name=s['name'], rating=s['rating']))
        db.session.commit()
        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for('login'))
    return render_template('register.html', skills=CREATIVE_SKILLS, form={})

@app.route('/dashboard')
@login_required
def dashboard():
    user = db.session.get(User, session['user_id'])
    return render_template('dashboard.html', user=user)

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    flash("You've been signed out. See you soon!", "success")
    return redirect(url_for('login'))

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
