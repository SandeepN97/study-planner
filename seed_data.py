"""Realistic sample assignments for demos. Due dates are relative to today so the
priority ranking always looks believable (some overdue, some due soon, some far off)."""
from datetime import date, datetime, timedelta

# (course, title, days from today, difficulty 1-5, done)
SAMPLES = [
    ("COMP3322", "Project proposal: requirements and scope", -2, 3, False),
    ("MATH2011", "Problem set 6: eigenvalues and diagonalization", -1, 4, False),
    ("STAT2601", "Lab report: hypothesis testing on survey data", 0, 3, False),
    ("COMP3322", "Sprint 2 demo and retrospective notes", 2, 4, False),
    ("ECON1210", "Reading response: supply shocks in 2022", 1, 1, False),
    ("PHYS1050", "Lab 4 write-up: pendulum and error analysis", 3, 2, False),
    ("ENGG1100", "Team design review slides", 4, 3, False),
    ("MATH2011", "Midterm review sheet", 6, 5, False),
    ("STAT2601", "Quiz 3 prep: confidence intervals", 7, 2, False),
    ("ECON1210", "Essay outline: minimum wage and employment", 9, 3, False),
    ("COMP3322", "Final report draft", 14, 5, False),
    ("PHYS1050", "Problem set 7: rotational dynamics", 12, 4, False),
    ("ENGG1100", "Safety module certificate", -6, 1, True),
    ("STAT2601", "Problem set 5: probability distributions", -4, 3, True),
    ("ECON1210", "Reading response: comparative advantage", -8, 1, True),
]


def insert_samples(db, owner):
    """Insert the sample rows for `owner` ('u:<id>', 'g:<token>', or None)."""
    now = datetime.now()
    for i, (course, title, offset, difficulty, done) in enumerate(SAMPLES):
        due = (date.today() + timedelta(days=offset)).isoformat()
        created = (now - timedelta(days=10, hours=i)).isoformat(timespec="seconds")
        db.execute(
            "INSERT INTO assignments (course, title, due_date, difficulty, done, created_at, owner) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (course, title, due, difficulty, int(done), created, owner),
        )
    return len(SAMPLES)
