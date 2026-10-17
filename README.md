# Student Study Planner

Flask + SQLite web app for COMP3322 (Software Engineering).

## Functionalities
1. **Add an assignment**: enter course, title, due date, and difficulty; it is saved to SQLite and a confirmation is shown.
2. **Search / filter + recommendation**: search by course or title, filter by status or due date. Assignments are ranked by a priority score (urgency + difficulty), and the home page recommends what to work on first.

## Run it
```bash
cd study-planner
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000

## Priority score
`score = urgency + difficulty * 2`, where urgency = `10 - days_left` (min 0), or 15 if overdue.

## 5-minute demo flow
1. Home page: explain the purpose
2. Add 2-3 assignments (show the confirmation message)
3. Return to home: show the recommendation and top priorities
4. Search & Filter: search by course, filter by due date, mark one done
5. Show `planner.db` (backend storage)

## Project layout
```
app.py              routes, database, priority logic
templates/          base, home, add, assignments
static/style.css    styling
planner.db          created automatically on first run
```
