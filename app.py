"""Student Study Planner - Flask + SQLite.

Functionality 1: Add an assignment (saved to SQLite, confirmation shown).
Functionality 2: Search/filter assignments + priority recommendation.
"""
import os
import sqlite3
from datetime import date, datetime

from flask import Flask, flash, g, redirect, render_template, request, url_for

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "planner.db")

app = Flask(__name__)
app.secret_key = "dev-secret-change-me"


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


# ---------- Routes ----------
@app.route("/")
def home():
    rows = get_db().execute("SELECT * FROM assignments WHERE done = 0").fetchall()
    items = sorted(with_priority(rows), key=lambda i: i["score"], reverse=True)
    total = get_db().execute("SELECT COUNT(*) FROM assignments").fetchone()[0]
    return render_template(
        "home.html",
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
            "INSERT INTO assignments (course, title, due_date, difficulty, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (course, title, due, difficulty, datetime.now().isoformat(timespec="seconds")),
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

    sql = "SELECT * FROM assignments WHERE 1=1"
    params = []
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
    db.execute("UPDATE assignments SET done = 1 - done WHERE id = ?", (aid,))
    db.commit()
    return redirect(request.referrer or url_for("assignments"))


@app.route("/delete/<int:aid>", methods=["POST"])
def delete(aid):
    db = get_db()
    db.execute("DELETE FROM assignments WHERE id = ?", (aid,))
    db.commit()
    flash("Assignment deleted.", "success")
    return redirect(request.referrer or url_for("assignments"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
