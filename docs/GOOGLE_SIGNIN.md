# Setting up "Sign in with Google"

Sign-in with Google is **optional**. Without it the app works as a guest-only app, and the button shows "not set up". Do this once if you want real Google sign-in.

## What you are creating

You are **not** giving the app your Google password. You are registering the app itself with Google and getting two values back:

| Value | What it is | Secret? |
| --- | --- | --- |
| **Client ID** | The app's public name tag. Google shows it as "Study Planner wants to see your name and email". | No |
| **Client secret** | Proves the server really is that app when it swaps Google's one-time code for the user's identity. | **Yes** |

Each person who later signs in uses their own Google account on Google's own page. The app never sees their password.

It is free and takes about 10 minutes. You need any Google account.

## Steps

### 1. Create a Google Cloud project

1. Open <https://console.cloud.google.com/> and sign in.
2. Click the project picker at the top → **New project**.
3. Name it `Study Planner` → **Create**, then make sure it is the selected project.

### 2. Configure the consent screen

1. Open **APIs & Services → OAuth consent screen** (in newer consoles this is called **Google Auth Platform**; click **Get started**).
2. App name: `Study Planner`. User support email: your email.
3. Audience / user type: **External**.
4. Developer contact email: your email → finish and **Create**.
5. Open **Audience** (or **Test users** in the older console) and **add the Google accounts that should be able to sign in** while the app is in testing mode. Include your own.

> In testing mode only the listed test users can sign in. That is fine for a course project or demo. Publishing the app for everyone requires Google's verification and isn't needed here.

### 3. Create the OAuth client

1. Open **APIs & Services → Credentials** (or **Google Auth Platform → Clients**).
2. **Create credentials → OAuth client ID** (or **Create client**).
3. Application type: **Web application**. Name: `Study Planner local`.
4. Under **Authorized redirect URIs** click **Add URI** and enter exactly:

   ```
   http://127.0.0.1:5000/auth/callback
   ```

   It must match character for character: `http`, `127.0.0.1` (not `localhost`), port `5000`, and the path.
5. Click **Create**.
6. Copy the **Client ID** (ends in `.apps.googleusercontent.com`) and the **Client secret**. You can view them again later from the Credentials page.

### 4. Put them in the app

In the project folder:

```bash
cp .env.example .env
```

Open `.env` in any editor and fill in the two lines:

```
GOOGLE_CLIENT_ID=1234567890-abc123.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-xxxxxxxxxxxxxxxxxxxx
```

Save the file. `.env` is git-ignored, so it will not be committed.

### 5. Restart and test

1. Stop the app (`Ctrl+C`) and start it again: `python app.py`.
2. Open **http://127.0.0.1:5000** (use `127.0.0.1`, not `localhost`).
3. Click **Sign in with Google**, choose a test-user account, and approve.
4. You land on the dashboard with your name in the top-right corner. Click **Sign out** to leave.

## What happens to existing data

- Assignments you added as a **guest** move to your account when you sign in.
- Assignments from before accounts existed (older `planner.db` files) are given to the **first person who signs in**.

## Troubleshooting

| Problem | Fix |
| --- | --- |
| Button says "Sign in with Google (not set up)" | `.env` is missing or a value is blank. Check both lines are filled, there are no quotes or spaces around the values, and restart the app. |
| Error `redirect_uri_mismatch` on Google's page | The redirect URI in Google Cloud doesn't exactly match. It must be `http://127.0.0.1:5000/auth/callback`, and you must open the app at `127.0.0.1`, not `localhost`. Changes can take a few minutes to apply. |
| Error `access_denied` / "app not verified" / "has not completed verification" | Your account isn't listed as a test user. Add it under **Audience → Test users**. |
| "Google sign-in was cancelled or failed" banner | You closed the Google page or denied access. Click the button and try again. |
| Works on `127.0.0.1:5000` but you run on another port or host | Add that exact URI too under **Authorized redirect URIs** (for example `http://127.0.0.1:5001/auth/callback`). |
| Want to use a deployed URL | Add `https://your-domain/auth/callback` as another authorized redirect URI. Google requires `https` for anything that isn't localhost. |

## Keeping it safe

- Never commit `.env` or paste the client secret into code, chat or screenshots.
- If the secret leaks, open the client on the Credentials page and **Reset secret** (or create a new client), then update `.env`.
- The app only requests your name, email and profile picture (`openid email profile`) and stores just those.
