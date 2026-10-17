"""Fill planner.db with realistic sample assignments.

    python seed.py            add the samples (owner-less: the first person to sign in
                              with Google receives them)
    python seed.py --reset    first delete all owner-less rows, then add the samples

Guests can also click "Load sample data" on the empty dashboard instead.
"""
import sqlite3
import sys

from app import DATABASE, init_db
from seed_data import insert_samples


def main():
    init_db()
    with sqlite3.connect(DATABASE) as db:
        if "--reset" in sys.argv:
            removed = db.execute("DELETE FROM assignments WHERE owner IS NULL").rowcount
            print(f"Removed {removed} owner-less row(s).")
        count = insert_samples(db, None)
    print(f"Added {count} sample assignments to {DATABASE}.")
    print("They belong to no one yet: the first Google sign-in adopts them.")


if __name__ == "__main__":
    main()
