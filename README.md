# Student Study Planner

A small Flask + SQLite web app for tracking assignments and deciding what to work on first. Built for COMP3322 (Software Engineering).

## Features

1. **Add an assignment** – enter course, title, due date, and difficulty (1–5). It is saved to SQLite and a confirmation message is shown.
2. **Search, filter, and recommendation** – search by course or title, filter by status (pending / done / all) or due date. Assignments are ranked by a priority score, and the home page recommends what to tackle first.
3. Mark assignments done (or undo) and delete them.

## Requirements

- Python 3.9 or newer (check with `python3 --version`)
- pip
- No other setup: SQLite ships with Python, and the only dependency is Flask (`Flask>=3.0`)

## Quick start

```bash
git clone https://github.com/SandeepN97/study-planner.git
cd study-planner

python3 -m venv venv
source venv/bin/activate        # Windows (PowerShell): venv\Scripts\Activate.ps1
                                # Windows (cmd):        venv\Scripts\activate.bat

pip install -r requirements.txt
python app.py
```

Then open **http://127.0.0.1:5000** in your browser.

Stop the server with `Ctrl+C`. Deactivate the virtual environment with `deactivate`.

> On macOS/Linux use `python3` if `python` is not found. Inside an activated venv, `python` works.

## How it runs

- `python app.py` creates `planner.db` automatically on first run (via `init_db()`) and starts Flask in debug mode with auto-reload on port 5000.
- Always start it with `python app.py`. Running it with `flask run` skips `init_db()`, so the `assignments` table will not exist and pages will error.
- To reset all data, stop the server and delete `planner.db`; it is recreated on the next start.

### Troubleshooting

| Problem | Fix |
| --- | --- |
| `ModuleNotFoundError: No module named 'flask'` | The venv is not active or dependencies are not installed. Run `source venv/bin/activate` then `pip install -r requirements.txt`. |
| `Address already in use` (port 5000) | On macOS, AirPlay Receiver uses port 5000. Turn it off in System Settings → General → AirDrop & Handoff, or change the port in the last line of `app.py`: `app.run(debug=True, port=5001)`. |
| `no such table: assignments` | You started the app without `python app.py`. Start it that way (see above). |
| `command not found: python` | Use `python3` instead. |

## Using the app

| Page | URL | What it does |
| --- | --- | --- |
| Home | `/` | Shows counts, the recommended next assignment, and the top 5 priorities |
| Add | `/add` | Form to add an assignment; shows a confirmation on success |
| Search & Filter | `/assignments` | Search by course/title, filter by status and due date, mark done, delete |

### Priority score

```
score = urgency + difficulty * 2
urgency = 15                      if overdue
urgency = max(0, 10 - days_left)  otherwise
```

Higher score means work on it sooner. Only pending (not done) assignments are recommended on the home page.

## Project layout

```
app.py              routes, database access, priority logic
requirements.txt    Python dependencies (Flask)
templates/          base.html, home.html, add.html, assignments.html
static/style.css    styling
planner.db          SQLite database, created automatically on first run
```

## 5-minute demo flow

1. Home page: explain the purpose
2. Add 2–3 assignments (show the confirmation message)
3. Return to home: show the recommendation and top priorities
4. Search & Filter: search by course, filter by due date, mark one done
5. Show `planner.db` (backend storage), e.g. `sqlite3 planner.db "SELECT * FROM assignments;"`
