# Student Study Planner

A small Flask + SQLite web app for tracking assignments and deciding what to work on first. Built for COMP3322 (Software Engineering).

## Features

1. **Add an assignment** – enter course, title, due date, and difficulty (1–5). It is saved to SQLite and a confirmation message is shown.
2. **Search, filter, and recommendation** – search by course or title, filter by status (pending / done / all) or due date. Assignments are ranked by a priority score, and the home page recommends what to tackle first.
3. Mark assignments done (or undo) and delete them.
4. **Landing page and accounts** – a public home page at `/`. Use the app as a guest right away, or sign in with Google to keep your assignments on your account. Guest assignments move to your account when you sign in.

## Prerequisites

You need four things: **Git**, **Python 3.9+**, **pip**, and **venv** (Python's virtual-environment module). SQLite ships with Python, and the only package dependency is Flask (`Flask>=3.0`), which `pip` installs for you.

### 1. Check what you already have

```bash
git --version
python3 --version      # Windows: python --version  (or: py --version)
pip3 --version         # Windows: pip --version     (or: py -m pip --version)
```

Each should print a version. Python must be 3.9 or newer. If a command says "not found", install that item below.

### 2. Install Git (if missing)

| OS | Command / link |
| --- | --- |
| macOS | `xcode-select --install` (or `brew install git`) |
| Ubuntu / Debian | `sudo apt update && sudo apt install -y git` |
| Fedora | `sudo dnf install -y git` |
| Windows | Download from <https://git-scm.com/download/win> and run the installer with the defaults |

Git is optional. If you don't want to install it, use "Option B – without Git" in [Step 1 of the Quick start](#step-1-get-the-code) to download the project as a ZIP instead.

### 3. Install Python (if missing or older than 3.9)

| OS | Steps |
| --- | --- |
| macOS | Download the installer from <https://www.python.org/downloads/macos/>, or run `brew install python` if you use [Homebrew](https://brew.sh) |
| Ubuntu / Debian | `sudo apt update && sudo apt install -y python3 python3-pip python3-venv` |
| Fedora | `sudo dnf install -y python3 python3-pip` |
| Windows | Download from <https://www.python.org/downloads/windows/>. **On the first installer screen, tick "Add python.exe to PATH"**, then click Install Now |

Close and reopen your terminal afterwards, then re-run the version checks from step 1.

### 4. Install pip (if missing)

pip is bundled with Python from python.org and Homebrew, so you usually already have it. If `pip3 --version` fails:

```bash
python3 -m ensurepip --upgrade        # works on most installs
```

If that reports `ensurepip` is unavailable (common on Ubuntu/Debian):

```bash
sudo apt install -y python3-pip       # Ubuntu / Debian
sudo dnf install -y python3-pip       # Fedora
```

Last resort, on any OS:

```bash
curl -O https://bootstrap.pypa.io/get-pip.py
python3 get-pip.py
```

Windows equivalent: `py -m ensurepip --upgrade`.

If `pip3` isn't found but `python3 -m pip --version` works, use `python3 -m pip` everywhere this README says `pip`.

### 5. Make sure venv works (Ubuntu / Debian only)

Debian-based systems ship Python without `venv`. If `python3 -m venv venv` later fails with "ensurepip is not available", run:

```bash
sudo apt install -y python3-venv
```

## Quick start

### Step 1: Get the code

**Option A – with Git** (Git installed):

```bash
git clone https://github.com/SandeepN97/study-planner.git
cd study-planner
```

**Option B – without Git** (no installation needed):

1. Open <https://github.com/SandeepN97/study-planner> in your browser.
2. Click the green **Code** button, then **Download ZIP**.
3. Unzip it. This creates a folder named `study-planner-main`.
4. Open a terminal in that folder:
   - **macOS:** right-click the folder → **New Terminal at Folder** (or `cd ~/Downloads/study-planner-main`)
   - **Windows:** open the folder in File Explorer, click the address bar, type `cmd`, press Enter (or `cd %USERPROFILE%\Downloads\study-planner-main`)
   - **Linux:** `cd ~/Downloads/study-planner-main`

Prefer the command line? This also works without Git, on macOS/Linux and Windows 10+ (the built-in `curl` and `tar`):

```bash
curl -L -o study-planner.tar.gz https://github.com/SandeepN97/study-planner/archive/refs/heads/main.tar.gz
tar -xzf study-planner.tar.gz
cd study-planner-main
```

Confirm you are in the right folder by checking that `app.py` is listed (`ls` on macOS/Linux, `dir` on Windows).

### Step 2: Set up and run

From inside the project folder (the one containing `app.py`):

```bash
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
- The database tables are created (and older databases migrated) automatically when the app starts, however you start it (`python app.py` or `flask run`).
- To reset all data, stop the server and delete `planner.db`; it is recreated on the next start.

### Troubleshooting

| Problem | Fix |
| --- | --- |
| `ModuleNotFoundError: No module named 'flask'` | The venv is not active or dependencies are not installed. Run `source venv/bin/activate` then `pip install -r requirements.txt`. |
| `Address already in use` (port 5000) | On macOS, AirPlay Receiver uses port 5000. Turn it off in System Settings → General → AirDrop & Handoff, or change the port in the last line of `app.py`: `app.run(debug=True, port=5001)`. |
| `command not found: python` | Use `python3` instead (Windows: `py`). |
| `pip: command not found` | See [Install pip](#4-install-pip-if-missing), or use `python3 -m pip install -r requirements.txt`. |
| `python3 -m venv venv` fails with "ensurepip is not available" | Ubuntu/Debian: `sudo apt install -y python3-venv`. |
| `error: externally-managed-environment` when running pip | You are outside the venv. Run `source venv/bin/activate` first, then retry. |
| PowerShell: "running scripts is disabled" on `Activate.ps1` | Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, or use `venv\Scripts\activate.bat` in cmd. |
| `python` opens the Microsoft Store (Windows) | Python isn't installed or isn't on PATH. Reinstall from python.org and tick "Add python.exe to PATH". |

## Sign in with Google (optional)

The app works without this: everyone can use it as a guest, and the "Sign in with Google" button shows as "not set up". To switch it on you need your own Google OAuth credentials (Google issues these per app, so they can't be shipped in the repo).

1. Go to <https://console.cloud.google.com/> and create a project (or pick one).
2. **APIs & Services → OAuth consent screen**: choose **External**, fill in the app name and your email, and add your Google account under **Test users** while the app is in testing mode.
3. **APIs & Services → Credentials → Create credentials → OAuth client ID**, application type **Web application**.
4. Under **Authorized redirect URIs** add exactly: `http://127.0.0.1:5000/auth/callback`
5. Copy the **Client ID** and **Client secret**.
6. In the project folder, copy the example file and paste the values in:

```bash
cp .env.example .env
# edit .env and set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET
```

7. Restart the app and open **http://127.0.0.1:5000** (use `127.0.0.1`, not `localhost`, so it matches the redirect URI).

`.env` and the auto-generated `.secret_key` are git-ignored. Never commit them. Existing assignments from before accounts existed are given to the first person who signs in.

## Using the app

| Page | URL | What it does |
| --- | --- | --- |
| Home | `/` | Landing page: what the app does, sign in with Google or continue as guest |
| Dashboard | `/dashboard` | Shows counts, the recommended next assignment, and the top 5 priorities |
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
app.py              routes, database access, priority logic, Google sign-in
.env.example        template for Google credentials (copy to .env)
requirements.txt    Python dependencies (Flask)
templates/          base, landing, dashboard, add, assignments, Google button partial
static/style.css    styling
planner.db          SQLite database, created automatically on first run
```

## 5-minute demo flow

1. Home page: explain the purpose
2. Add 2–3 assignments (show the confirmation message)
3. Return to home: show the recommendation and top priorities
4. Search & Filter: search by course, filter by due date, mark one done
5. Show `planner.db` (backend storage), e.g. `sqlite3 planner.db "SELECT * FROM assignments;"`
