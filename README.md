# 🎓 SkillEnroll — Creative Skills Enrollment System

A full-stack web application built with **Python Flask** + **SQLite** that allows students to register with their college details and rate their creative skills using a star rating system.

## Features
- Student enrollment with full form validation
- Secure login/logout with hashed passwords
- Star rating (1–5) for 10 creative skills
- Personal dashboard showing profile + skills
- SQLite database — no extra setup needed

## Tech Stack
- **Backend:** Python Flask, SQLAlchemy
- **Database:** SQLite
- **Frontend:** Jinja2 templates, custom CSS
- **Deployment:** Render

## Run Locally

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/enrollment-project.git
cd enrollment-project

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python app.py

# Visit → http://127.0.0.1:5000
```

## Deploy to Render
1. Push this repo to GitHub
2. Go to render.com → New Web Service → Connect repo
3. Set Build Command: `pip install -r requirements.txt`
4. Set Start Command: `gunicorn app:app`
5. Add environment variable: `SECRET_KEY` = any long random string
6. Deploy!

## Pages
| Route | Description |
|---|---|
| `/` | Redirects to login or dashboard |
| `/login` | Sign in page |
| `/register` | Enrollment form with skill ratings |
| `/dashboard` | Profile view after login |
| `/logout` | Clears session |
