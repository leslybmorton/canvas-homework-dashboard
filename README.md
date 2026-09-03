# Canvas Homework Dashboard — Friends & Family Version

This version is designed so different people can open the same dashboard and connect their own Canvas account.

## What changed

- No Canvas token is stored in `.env`.
- Each person enters their own Canvas URL and token in the browser.
- The token is kept only in that person's active Streamlit session.
- Each person's Canvas data is cached only in that session.
- The dashboard automatically checks again about every 5 minutes while the tab is open.
- A manual **Refresh Canvas now** button is also available.
- The front page includes instructions for generating a Canvas access token.

## Run locally on Windows

1. Install Python 3.11 or newer.
2. Extract this ZIP.
3. Double-click `START_DASHBOARD.bat`.
4. Leave the black command window open while using the dashboard.

## Sharing with friends/family

Running this on your own computer only makes it available on your own computer by default.

To let friends/family open it over the internet, the app still needs to be hosted somewhere.
For a small private test, Streamlit Community Cloud or another simple Python host can work.

Before public hosting:
- Keep the source repository free of tokens and passwords.
- Use HTTPS.
- Do not log tokens.
- Keep this "session-only token" model or move to Canvas OAuth later.

## How users get a Canvas token

In Canvas, logged in as the student:

1. Account
2. Settings
3. Approved Integrations
4. + New Access Token
5. Enter a purpose such as "Homework Dashboard"
6. Select an expiration date if required
7. Generate Token
8. Copy it immediately

Some schools disable manual tokens. Those users would need a future OAuth version instead.

## Refresh behavior

The page automatically reruns about every 5 minutes while it is open.
The per-session cache also expires after 5 minutes.
The **Refresh Canvas now** button clears the cache immediately.
