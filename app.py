"""Student Study Planner - Flask + SQLite.

Functionality 1: Add an assignment (saved to SQLite, confirmation shown).
Functionality 2: Search/filter assignments + priority recommendation.
Accounts: optional "Sign in with Google"; everyone else uses the app as a guest.
"""
import os
import secrets
import sqlite3
from datetime import date, datetime, timedelta

from authlib.integrations.flask_client import OAuth, OAuthError
from dotenv import load_dotenv
from flask import (Flask, flash, g, redirect, render_template, request, session,
                   url_for)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

DATABASE = os.path.join(BASE_DIR, "planner.db")
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "").strip()
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "").strip()
GOOGLE_ENABLED = bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET)


def load_secret_key():
    """SECRET_KEY from the environment, else a random key persisted in .secret_key."""
    key = os.environ.get("SECRET_KEY", "").strip()
    if key:
        return key
    path = os.path.join(BASE_DIR, ".secret_key")
    if os.path.exists(path):
        with open(path) as f:
            return f.read().strip()
    key = secrets.token_hex(32)
    with open(path, "w") as f:
        f.write(key)
    os.chmod(path, 0o600)
    return key


app = Flask(__name__)
app.secret_key = load_secret_key()
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    PERMANENT_SESSION_LIFETIME=timedelta(days=60),
)

oauth = OAuth(app)
if GOOGLE_ENABLED:
    oauth.register(
        name="google",
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )


# ---------- Database helpers ----------
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    with sqlite3.connect(DATABASE) as db:
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course TEXT NOT NULL,
                title TEXT NOT NULL,
                due_date TEXT NOT NULL,
                difficulty INTEGER NOT NULL CHECK (difficulty BETWEEN 1 AND 5),
                done INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            )
            """
        )
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                google_sub TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL,
                name TEXT NOT NULL,
                picture TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        # Migration: older databases have no owner column. Rows with a NULL owner
        # are adopted by the first user who signs in with Google.
        cols = [r[1] for r in db.execute("PRAGMA table_info(assignments)")]
        if "owner" not in cols:
            db.execute("ALTER TABLE assignments ADD COLUMN owner TEXT")
        db.execute("CREATE INDEX IF NOT EXISTS idx_assignments_owner ON assignments (owner)")


init_db()


# ---------- Identity: Google user or guest ----------
def current_owner():
    """Owner key for assignment rows: 'u:<id>' for Google users, 'g:<token>' for guests."""
    if g.user is not None:
        return f"u:{g.user['id']}"
    token = session.get("guest")
    if not token:
        token = session["guest"] = secrets.token_urlsafe(16)
        session.permanent = True
    return f"g:{token}"


@app.before_request
def load_user():
    g.user = None
    uid = session.get("user_id")
    if uid:
        g.user = get_db().execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()
        if g.user is None:  # user row vanished (e.g. database reset)
            session.pop("user_id", None)


@app.context_processor
def inject_identity():
    return {"user": g.get("user"), "google_enabled": GOOGLE_ENABLED}


# ---------- Priority logic ----------
def priority_score(due_date_str, difficulty):
    """Higher score = work on it sooner. Combines urgency and difficulty."""
    days_left = (datetime.strptime(due_date_str, "%Y-%m-%d").date() - date.today()).days
    if days_left < 0:
        urgency = 15  # overdue
    else:
        urgency = max(0, 10 - days_left)
    return urgency + difficulty * 2


def days_left(due_date_str):
    return (datetime.strptime(due_date_str, "%Y-%m-%d").date() - date.today()).days


def with_priority(rows):
    items = []
    for r in rows:
        d = dict(r)
        d["days_left"] = days_left(d["due_date"])
        d["score"] = priority_score(d["due_date"], d["difficulty"])
        items.append(d)
    return items


# ---------- Auth routes ----------
@app.route("/login")
def login():
    if not GOOGLE_ENABLED:
        flash("Google sign-in isn't set up on this server yet. You can keep using the app as a guest.", "error")
        return redirect(url_for("home"))
    return oauth.google.authorize_redirect(url_for("auth_callback", _external=True))


@app.route("/auth/callback")
def auth_callback():
    if not GOOGLE_ENABLED:
        return redirect(url_for("home"))
    try:
        token = oauth.google.authorize_access_token()
    except OAuthError:
        flash("Google sign-in was cancelled or failed. Please try again.", "error")
        return redirect(url_for("home"))

    info = token.get("userinfo") or {}
    if not info.get("sub") or not info.get("email") or not info.get("email_verified", False):
        flash("Google did not return a verified email address.", "error")
        return redirect(url_for("home"))

    db = get_db()
    is_first_user = db.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0
    db.execute(
        "INSERT INTO users (google_sub, email, name, picture, created_at) VALUES (?, ?, ?, ?, ?) "
        "ON CONFLICT(google_sub) DO UPDATE SET email = excluded.email, "
        "name = excluded.name, picture = excluded.picture",
        (
            info["sub"],
            info["email"],
            info.get("name") or info["email"].split("@")[0],
            info.get("picture"),
            datetime.now().isoformat(timespec="seconds"),
        ),
    )
    user_id = db.execute("SELECT id FROM users WHERE google_sub = ?", (info["sub"],)).fetchone()[0]
    owner = f"u:{user_id}"

    # Keep what the person added as a guest.
    guest = session.get("guest")
    if guest:
        db.execute("UPDATE assignments SET owner = ? WHERE owner = ?", (owner, f"g:{guest}"))
    # Rows from before accounts existed go to the first person to sign in.
    if is_first_user:
        db.execute("UPDATE assignments SET owner = ? WHERE owner IS NULL", (owner,))
    db.commit()

    session.clear()
    session["user_id"] = user_id
    session.permanent = True
    flash(f"Signed in as {info['email']}.", "success")
    return redirect(url_for("dashboard"))


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("Signed out.", "success")
    return redirect(url_for("home"))


# ---------- Routes ----------
@app.route("/")
def home():
    has_session = g.user is not None or "guest" in session
    return render_template("landing.html", has_session=has_session)


@app.route("/dashboard")
def dashboard():
    owner = current_owner()
    db = get_db()
    rows = db.execute("SELECT * FROM assignments WHERE done = 0 AND owner = ?", (owner,)).fetchall()
    items = sorted(with_priority(rows), key=lambda i: i["score"], reverse=True)
    total = db.execute("SELECT COUNT(*) FROM assignments WHERE owner = ?", (owner,)).fetchone()[0]
    return render_template(
        "dashboard.html",
        recommended=items[0] if items else None,
        top=items[:5],
        pending=len(items),
        total=total,
    )


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        course = request.form.get("course", "").strip()
        title = request.form.get("title", "").strip()
        due = request.form.get("due_date", "").strip()
        difficulty = request.form.get("difficulty", "3")

        error = None
        if not course or not title or not due:
            error = "Course, title, and due date are required."
        else:
            try:
                datetime.strptime(due, "%Y-%m-%d")
                difficulty = int(difficulty)
                if not 1 <= difficulty <= 5:
                    raise ValueError
            except ValueError:
                error = "Please enter a valid date and a difficulty from 1 to 5."

        if error:
            flash(error, "error")
            return render_template("add.html", form=request.form), 400

        db = get_db()
        db.execute(
            "INSERT INTO assignments (course, title, due_date, difficulty, created_at, owner) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (course, title, due, difficulty, datetime.now().isoformat(timespec="seconds"),
             current_owner()),
        )
        db.commit()
        flash(f'Saved! "{title}" for {course} is due {due}.', "success")
        return redirect(url_for("add"))

    return render_template("add.html", form={})


@app.route("/assignments")
def assignments():
    q = request.args.get("q", "").strip()
    status = request.args.get("status", "pending")
    due_before = request.args.get("due_before", "").strip()

    sql = "SELECT * FROM assignments WHERE owner = ?"
    params = [current_owner()]
    if q:
        sql += " AND (course LIKE ? OR title LIKE ?)"
        params += [f"%{q}%", f"%{q}%"]
    if status == "pending":
        sql += " AND done = 0"
    elif status == "done":
        sql += " AND done = 1"
    if due_before:
        sql += " AND due_date <= ?"
        params.append(due_before)

    rows = get_db().execute(sql, params).fetchall()
    items = sorted(with_priority(rows), key=lambda i: i["score"], reverse=True)
    return render_template(
        "assignments.html", items=items, q=q, status=status, due_before=due_before
    )


@app.route("/toggle/<int:aid>", methods=["POST"])
def toggle(aid):
    db = get_db()
    db.execute("UPDATE assignments SET done = 1 - done WHERE id = ? AND owner = ?",
               (aid, current_owner()))
    db.commit()
    return redirect(request.referrer or url_for("assignments"))


@app.route("/delete/<int:aid>", methods=["POST"])
def delete(aid):
    db = get_db()
    db.execute("DELETE FROM assignments WHERE id = ? AND owner = ?", (aid, current_owner()))
    db.commit()
    flash("Assignment deleted.", "success")
    return redirect(request.referrer or url_for("assignments"))


if __name__ == "__main__":
    app.run(debug=True)
