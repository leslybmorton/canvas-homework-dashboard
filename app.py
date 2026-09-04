import os
import time
from datetime import datetime
from zoneinfo import ZoneInfo
from urllib.parse import urlparse

import pandas as pd
import requests
import streamlit as st
from streamlit_autorefresh import st_autorefresh

st.set_page_config(
    page_title="Canvas Homework Dashboard",
    page_icon="📚",
    layout="wide",
)


st.markdown(
    """
    <style>
    /* Overall page spacing */
    .block-container {
        padding-top: 1.4rem;
        padding-bottom: 3rem;
        max-width: 1500px;
    }

    /* Hide Streamlit chrome clutter */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Header / hero card */
    .dashboard-hero {
        background: linear-gradient(135deg, #F7F2EA 0%, #EFE7DC 100%);
        border: 1px solid rgba(60, 87, 99, 0.18);
        border-radius: 22px;
        padding: 1.35rem 1.5rem;
        margin: 0 0 1.25rem 0;
        box-shadow: 0 8px 22px rgba(61, 52, 47, 0.07);
    }

    .dashboard-hero h1 {
        margin: 0;
        color: #3C5763;
        font-size: 2.1rem;
        line-height: 1.15;
    }

    .dashboard-hero p {
        margin: .45rem 0 0 0;
        color: #6A5E57;
        font-size: 1rem;
    }

    /* Section headings */
    h2, h3 {
        color: #3C5763 !important;
        letter-spacing: -0.02em;
    }

    /* Buttons */
    .stButton > button,
    .stFormSubmitButton > button {
        border-radius: 12px !important;
        border: 1px solid #3C5763 !important;
        font-weight: 650 !important;
        min-height: 2.6rem;
        transition: all .15s ease-in-out;
    }

    .stButton > button:hover,
    .stFormSubmitButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 5px 14px rgba(60, 87, 99, 0.16);
    }


    /* Metrics as cards */
    div[data-testid="stMetric"] {
        background: #FFFDF9;
        border: 1px solid rgba(60, 87, 99, 0.16);
        border-radius: 16px;
        padding: 1rem 1.05rem;
        box-shadow: 0 4px 14px rgba(61, 52, 47, 0.05);
    }

    div[data-testid="stMetricLabel"] {
        color: #6A5E57;
        font-weight: 600;
    }

    div[data-testid="stMetricValue"] {
        color: #3C5763;
    }

    /* Alerts */
    div[data-testid="stAlert"] {
        border-radius: 14px;
    }

    /* Dataframes */
    div[data-testid="stDataFrame"] {
        border: 1px solid rgba(60, 87, 99, 0.14);
        border-radius: 14px;
        overflow: hidden;
        box-shadow: 0 4px 14px rgba(61, 52, 47, 0.04);
    }

    /* Expanders */
    div[data-testid="stExpander"] {
        border-radius: 14px;
        border-color: rgba(60, 87, 99, 0.16);
        overflow: hidden;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        border-right: 1px solid rgba(60, 87, 99, 0.12);
    }

    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #3C5763 !important;
    }

    /* Soft divider */
    hr {
        border-color: rgba(60, 87, 99, 0.12);
    }

    /* Small badge style used in custom HTML */
    .soft-badge {
        display: inline-block;
        background: #E9F0F2;
        color: #3C5763;
        border-radius: 999px;
        padding: .28rem .65rem;
        font-size: .82rem;
        font-weight: 650;
        margin-right: .35rem;
    }

    /* Landing instruction card */
    .instruction-card {
        background: #FFFDF9;
        border: 1px solid rgba(60, 87, 99, 0.14);
        border-radius: 18px;
        padding: 1.1rem 1.25rem;
        box-shadow: 0 5px 16px rgba(61, 52, 47, 0.05);
        margin-bottom: .8rem;
    }

    /* FORCE CONSISTENT LIGHT COZY THEME */
    html, body, [data-testid="stAppViewContainer"], .stApp {
        background: #F7F2EA !important;
        color: #3D342F !important;
    }

    [data-testid="stHeader"] {
        background: rgba(247, 242, 234, 0.96) !important;
    }

    /* Main text */
    .stMarkdown, .stMarkdown p, .stMarkdown li,
    .stText, label, .stCaption, small,
    div[data-testid="stMarkdownContainer"] {
        color: #3D342F !important;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #EFE7DC !important;
    }

    section[data-testid="stSidebar"] * {
        color: #3D342F !important;
    }

    /* Cards / forms / expanders */
    div[data-testid="stForm"],
    div[data-testid="stExpander"],
    div[data-testid="stMetric"],
    .instruction-card {
        background: #FFFDF9 !important;
        color: #3D342F !important;
    }

    /* Expander title and content */
    div[data-testid="stExpander"] summary,
    div[data-testid="stExpander"] summary *,
    div[data-testid="stExpander"] div,
    div[data-testid="stExpander"] p,
    div[data-testid="stExpander"] li {
        color: #3D342F !important;
    }


    /* Primary buttons - kill the red */
    button[kind="primary"],
    .stFormSubmitButton > button,
    .stButton > button[kind="primary"] {
        background: #3C5763 !important;
        color: #FFFFFF !important;
        border-color: #3C5763 !important;
    }

    button[kind="primary"]:hover,
    .stFormSubmitButton > button:hover,
    .stButton > button[kind="primary"]:hover {
        background: #2F4650 !important;
        color: #FFFFFF !important;
        border-color: #2F4650 !important;
    }

    /* Secondary buttons */
    .stButton > button:not([kind="primary"]) {
        background: #FFFDF9 !important;
        color: #3C5763 !important;
        border-color: #3C5763 !important;
    }

    /* Fix hero and private-session card text visibility */
    .dashboard-hero,
    .dashboard-hero *,
    .instruction-card,
    .instruction-card * {
        color: #3D342F !important;
    }

    .dashboard-hero h1 {
        color: #3C5763 !important;
    }

    .soft-badge {
        background: #E5EEF1 !important;
        color: #3C5763 !important;
    }

    /* Warning/info/success alerts with readable light backgrounds */
    div[data-testid="stAlert"] {
        color: #3D342F !important;
    }

    div[data-testid="stAlert"] * {
        color: inherit !important;
    }

    /* Tables */
    div[data-testid="stDataFrame"] {
        background: #FFFDF9 !important;
    }

    /* Links */
    a {
        color: #3C5763 !important;
    }



    /* Safer Streamlit widget styling for Community Cloud */
    div[data-testid="stTextInput"] input {
        background: #FFFDF9 !important;
        color: #3D342F !important;
        border-radius: 10px !important;
    }

    div[data-testid="stTextInput"] input::placeholder {
        color: #8A7D74 !important;
        opacity: 1 !important;
    }

    div[data-testid="stTextInput"] label,
    div[data-testid="stSelectbox"] label {
        color: #3D342F !important;
        font-weight: 600 !important;
    }

    div[data-testid="stSelectbox"] > div > div {
        border-radius: 10px !important;
    }

    /* Final contrast fixes */
    div[data-testid="stExpander"] summary {
        background: #E5EEF1 !important;
        border-radius: 12px !important;
    }

    div[data-testid="stExpander"] summary,
    div[data-testid="stExpander"] summary *,
    div[data-testid="stExpander"] summary p,
    div[data-testid="stExpander"] summary span {
        color: #3C5763 !important;
        font-weight: 700 !important;
    }

    /* Keep all primary action button text white */
    button[kind="primary"],
    button[kind="primary"] *,
    .stFormSubmitButton > button,
    .stFormSubmitButton > button *,
    .stButton > button[kind="primary"],
    .stButton > button[kind="primary"] * {
        color: #FFFFFF !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

DEFAULT_TZ = "America/Los_Angeles"
CACHE_TTL_SECONDS = 300  # 5 minutes


class CanvasError(Exception):
    pass


# ----------------------------
# Session-only connection data
# ----------------------------
if "canvas_token" not in st.session_state:
    st.session_state.canvas_token = ""
if "canvas_base_url" not in st.session_state:
    st.session_state.canvas_base_url = ""
if "canvas_timezone" not in st.session_state:
    st.session_state.canvas_timezone = DEFAULT_TZ
if "data_cache" not in st.session_state:
    st.session_state.data_cache = {}
if "connected" not in st.session_state:
    st.session_state.connected = False


def normalize_canvas_url(value):
    value = (value or "").strip().rstrip("/")
    if not value:
        return ""
    if not value.startswith(("http://", "https://")):
        value = "https://" + value
    parsed = urlparse(value)
    if not parsed.netloc:
        return ""
    return f"{parsed.scheme}://{parsed.netloc}"


def token_fingerprint(token):
    # Used only as part of an in-memory cache key. The token itself is never displayed.
    if not token:
        return ""
    return f"{len(token)}:{token[:4]}:{token[-4:]}"


def headers():
    token = st.session_state.canvas_token
    if not token:
        raise CanvasError("No Canvas token is connected.")
    return {"Authorization": f"Bearer {token}"}


def canvas_get(path, params=None):
    base_url = st.session_state.canvas_base_url
    url = f"{base_url}{path}"
    r = requests.get(url, headers=headers(), params=params, timeout=30)
    if r.status_code == 401:
        raise CanvasError("Canvas rejected this token. It may be expired, revoked, or copied incorrectly.")
    if r.status_code == 403:
        raise CanvasError("Canvas accepted the login, but this account does not have permission for that request.")
    if not r.ok:
        raise CanvasError(f"Canvas returned HTTP {r.status_code}: {r.text[:300]}")
    return r


def canvas_get_all(path, params=None):
    params = dict(params or {})
    params.setdefault("per_page", 100)
    items = []
    url = f"{st.session_state.canvas_base_url}{path}"
    req_params = params

    while url:
        r = requests.get(url, headers=headers(), params=req_params, timeout=30)
        if r.status_code == 401:
            raise CanvasError("Canvas rejected this token. It may be expired, revoked, or copied incorrectly.")
        if r.status_code == 403:
            raise CanvasError("Canvas accepted the login, but this account does not have permission for that request.")
        if not r.ok:
            raise CanvasError(f"Canvas returned HTTP {r.status_code}: {r.text[:300]}")

        data = r.json()
        if isinstance(data, dict) and "value" in data and isinstance(data["value"], list):
            data = data["value"]
        if not isinstance(data, list):
            raise CanvasError("Canvas returned an unexpected response format.")

        items.extend(data)

        next_url = None
        link_header = r.headers.get("Link", "")
        for part in link_header.split(","):
            if 'rel="next"' in part:
                candidate = part.split(";")[0].strip()
                if candidate.startswith("<") and candidate.endswith(">"):
                    next_url = candidate[1:-1]
                    break

        url = next_url
        req_params = None

    return items


def parse_dt(value):
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt.astimezone(ZoneInfo(st.session_state.canvas_timezone))
    except Exception:
        return None


def fmt_dt(dt):
    if not dt:
        return "—"
    hour = dt.strftime("%I").lstrip("0") or "0"
    return f"{dt.strftime('%a %b')} {dt.day}, {hour}:{dt.strftime('%M %p')}"


def school_year_start(now):
    year = now.year if now.month >= 7 else now.year - 1
    return datetime(year, 7, 1, tzinfo=now.tzinfo)


def cache_key(prefix, extra=""):
    return "|".join([
        prefix,
        st.session_state.canvas_base_url,
        token_fingerprint(st.session_state.canvas_token),
        extra,
    ])


def session_cache_get(key):
    item = st.session_state.data_cache.get(key)
    if not item:
        return None
    if time.time() - item["saved_at"] > CACHE_TTL_SECONDS:
        st.session_state.data_cache.pop(key, None)
        return None
    return item["value"]


def session_cache_set(key, value):
    st.session_state.data_cache[key] = {"saved_at": time.time(), "value": value}


def clear_session_cache():
    st.session_state.data_cache = {}


def get_profile():
    key = cache_key("profile")
    cached = session_cache_get(key)
    if cached is not None:
        return cached
    value = canvas_get("/api/v1/users/self/profile").json()
    session_cache_set(key, value)
    return value


def get_courses(include_older=False):
    key = cache_key("courses", str(include_older))
    cached = session_cache_get(key)
    if cached is not None:
        return cached

    enrollments = canvas_get_all("/api/v1/users/self/enrollments")
    now = datetime.now(ZoneInfo(st.session_state.canvas_timezone))
    sy_start = school_year_start(now)

    current = []
    seen = set()

    for e in enrollments:
        if e.get("type") != "StudentEnrollment":
            continue
        if e.get("enrollment_state") not in ("active", "invited"):
            continue

        created = parse_dt(e.get("created_at"))
        if not include_older and (not created or created < sy_start):
            continue

        course_id = e.get("course_id")
        if not course_id or course_id in seen:
            continue

        try:
            c = canvas_get(f"/api/v1/courses/{course_id}").json()
        except CanvasError:
            continue

        seen.add(course_id)
        current.append({
            "id": course_id,
            "name": c.get("name") or c.get("course_code") or f"Course {course_id}",
            "course_code": c.get("course_code"),
            "enrollment_created_at": created,
        })

    value = sorted(current, key=lambda x: x["name"].lower())
    session_cache_set(key, value)
    return value


def get_assignments(course_id):
    key = cache_key("assignments", str(course_id))
    cached = session_cache_get(key)
    if cached is not None:
        return cached

    value = canvas_get_all(
        f"/api/v1/courses/{course_id}/assignments",
        params={"include[]": "submission", "per_page": 100},
    )
    session_cache_set(key, value)
    return value


def assignment_row(course, a, now):
    sub = a.get("submission") or {}
    due = parse_dt(a.get("due_at") or sub.get("cached_due_date"))
    unlock = parse_dt(a.get("unlock_at"))
    created = parse_dt(a.get("created_at"))
    assigned = unlock or created
    submitted_at = parse_dt(sub.get("submitted_at"))
    graded_at = parse_dt(sub.get("graded_at"))

    submission_types = a.get("submission_types") or []
    actionable = any(t not in ("none", "not_graded", "on_paper") for t in submission_types)

    workflow = (sub.get("workflow_state") or "").lower()
    submitted = bool(submitted_at) or workflow in ("submitted", "graded", "pending_review")

    missing = bool(sub.get("missing"))
    late = bool(sub.get("late"))

    if sub.get("excused"):
        status = "Excused"
    elif missing:
        status = "Missing"
    elif submitted and sub.get("grade") is not None:
        status = "Graded"
    elif submitted:
        status = "Submitted"
    elif not actionable and due:
        status = "No Canvas submission"
    elif due and due < now:
        status = "Overdue"
    elif due and due.date() == now.date():
        status = "Due today"
    elif due:
        status = "Upcoming"
    else:
        status = "No due date"

    score = sub.get("score")
    grade = sub.get("grade")
    points_possible = a.get("points_possible")
    pct = None
    if isinstance(score, (int, float)) and isinstance(points_possible, (int, float)) and points_possible:
        pct = round(score / points_possible * 100, 1)

    return {
        "Course": course["name"],
        "Assignment": a.get("name", "(Untitled)"),
        "Assigned / Available": fmt_dt(assigned),
        "Due": fmt_dt(due),
        "Due_dt": due,
        "Submitted?": "Yes" if submitted else ("N/A" if not actionable else "No"),
        "Submitted at": fmt_dt(submitted_at),
        "Late?": "Yes" if late else "No",
        "Missing?": "Yes" if missing else "No",
        "Grade": grade if grade is not None else "—",
        "Score": score if score is not None else "—",
        "Points possible": points_possible if points_possible is not None else "—",
        "Percent": f"{pct}%" if pct is not None else "—",
        "Status": status,
        "Graded at": fmt_dt(graded_at),
        "Submission types": ", ".join(submission_types) if submission_types else "—",
        "URL": a.get("html_url", ""),
        "_actionable": actionable,
        "_submitted": submitted,
        "_missing": missing,
    }


# ----------------------------
# Public landing / connection
# ----------------------------
if not st.session_state.connected:
    st.markdown(
        """
        <div class="dashboard-hero">
            <h1>📚 Canvas Homework Dashboard</h1>
            <p>A cleaner way to see what is missing, due soon, submitted, and graded across Canvas.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="instruction-card">
            <span class="soft-badge">Private session</span>
            <span class="soft-badge">5-minute refresh</span>\n            <span class="soft-badge">Cloud build 1.1</span>
            <p style="margin:.8rem 0 0 0;">
                Connect your Canvas account below. Your token is used only for this browser session
                and is not saved to a file by the dashboard.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("🔑 How to get your Canvas access token", expanded=True):
        st.markdown(
            """
**In Canvas, logged in as the student:**

1. Open **Account**.
2. Choose **Settings**.
3. Scroll to **Approved Integrations**.
4. Click **+ New Access Token**.
5. Give it a purpose, such as **Homework Dashboard**.
6. Choose an expiration date if Canvas requires one.
7. Click **Generate Token**.
8. **Copy the token immediately.** Canvas may only show the full token once.
9. Come back here and paste it into the **Canvas access token** box below.

**Your Canvas URL** is the web address you normally use to sign into Canvas.  
For example: `https://temecula.instructure.com`

If you do not see **+ New Access Token**, your school may have disabled manual access tokens.
            """
        )

    st.warning(
        "Treat a Canvas token like a password. Do not email it, post it, or share it with anyone. "
        "Only enter it into a dashboard you trust."
    )

    base_url = st.text_input(
        "Canvas URL",
        placeholder="https://your-school.instructure.com",
        help="Use the Canvas site you normally log into.",
        key="connect_canvas_url",
    )
    token = st.text_input(
        "Canvas access token",
        type="password",
        help="The token stays in this Streamlit session. It is not written to a file.",
        key="connect_canvas_token",
    )
    timezone = st.selectbox(
        "Time zone",
        [
            "America/Los_Angeles",
            "America/Denver",
            "America/Chicago",
            "America/New_York",
        ],
        index=0,
        key="connect_canvas_timezone",
    )

    submitted = st.button(
        "Connect to Canvas",
        type="primary",
        use_container_width=True,
        key="connect_canvas_button",
    )

    if submitted:
        normalized = normalize_canvas_url(base_url)
        if not normalized:
            st.error("Please enter a valid Canvas URL.")
            st.stop()
        if not token.strip():
            st.error("Please paste a Canvas access token.")
            st.stop()

        st.session_state.canvas_base_url = normalized
        st.session_state.canvas_token = token.strip()
        st.session_state.canvas_timezone = timezone
        clear_session_cache()

        try:
            profile = get_profile()
            st.session_state.connected = True
            st.rerun()
        except Exception as e:
            st.session_state.canvas_token = ""
            st.session_state.connected = False
            clear_session_cache()
            st.error(f"Could not connect: {e}")

    st.stop()

st.markdown(
    """
    <div class="dashboard-hero">
        <h1>📚 Canvas Homework Dashboard</h1>
        <p>Your Canvas assignments, prioritized so the important stuff is easy to spot.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Automatically rerun the app every 5 minutes while this browser tab is open.
st_autorefresh(interval=CACHE_TTL_SECONDS * 1000, key="canvas_auto_refresh")

try:
    profile = get_profile()
except Exception as e:
    st.error(str(e))
    st.session_state.connected = False
    st.stop()

display_name = profile.get("short_name") or profile.get("name") or "Canvas student"

top1, top2 = st.columns([4, 1])
with top1:
    st.caption(
        f"Connected for **{display_name}** · Automatically checks Canvas about every 5 minutes while this tab is open."
    )
with top2:
    if st.button("Disconnect", use_container_width=True):
        st.session_state.canvas_token = ""
        st.session_state.canvas_base_url = ""
        st.session_state.connected = False
        clear_session_cache()
        st.rerun()

with st.sidebar:
    st.header("Dashboard")
    if st.button("🔄 Refresh Canvas now", use_container_width=True):
        clear_session_cache()
        st.rerun()

    include_older = st.checkbox(
        "Include older active courses",
        value=False,
        help="Useful if your school leaves old enrollments marked active.",
    )

try:
    with st.spinner("Loading classes…"):
        courses = get_courses(include_older=include_older)
except Exception as e:
    st.error(str(e))
    st.stop()

if not courses:
    st.warning(
        "I connected to Canvas, but I couldn't find current-school-year student courses. "
        "Try turning on **Include older active courses** in the sidebar."
    )
    st.stop()

with st.sidebar:
    st.header("Courses")
    course_names = [c["name"] for c in courses]
    selected_names = st.multiselect("Show", course_names, default=course_names)

    st.header("Display")
    show_no_due = st.checkbox("Include assignments with no due date", value=False)
    show_no_canvas_submission = st.checkbox("Include 'No Canvas submission' items", value=True)

selected_courses = [c for c in courses if c["name"] in selected_names]

rows = []
now = datetime.now(ZoneInfo(st.session_state.canvas_timezone))

with st.spinner("Loading assignments…"):
    for course in selected_courses:
        try:
            assignments = get_assignments(course["id"])
            for a in assignments:
                # Hide clearly informational / non-graded Canvas pages by default.
                if a.get("grading_type") == "not_graded" and not a.get("due_at"):
                    continue
                rows.append(assignment_row(course, a, now))
        except Exception as e:
            st.warning(f"Could not load {course['name']}: {e}")

if not rows:
    st.info("No assignments matched the current filters.")
    st.stop()

df = pd.DataFrame(rows)

if not show_no_due:
    df = df[df["Due_dt"].notna()]

if not show_no_canvas_submission:
    df = df[df["Status"] != "No Canvas submission"]

st.subheader("What needs attention")
st.caption("Missing and overdue work first, then today and the next 7 days.")

attention = df[
    df["Status"].isin(["Missing", "Overdue", "Due today", "Upcoming"])
    & (~df["_submitted"])
].copy()

attention = attention[
    attention["Due_dt"].notna()
    & (attention["Due_dt"] <= now.replace(hour=23, minute=59, second=59) + pd.Timedelta(days=7))
]

status_order = {"Missing": 0, "Overdue": 1, "Due today": 2, "Upcoming": 3}
attention["_order"] = attention["Status"].map(status_order).fillna(9)
attention = attention.sort_values(["_order", "Due_dt", "Course", "Assignment"])

if attention.empty:
    st.success("Nothing urgent is showing in Canvas right now. 🎉")
else:
    c1, c2, c3 = st.columns(3)
    c1.metric("Missing / overdue", int(attention["Status"].isin(["Missing", "Overdue"]).sum()))
    c2.metric("Due today", int((attention["Status"] == "Due today").sum()))
    c3.metric("Next 7 days", int(len(attention)))

    st.dataframe(
        attention[
            ["Status", "Course", "Assignment", "Assigned / Available", "Due", "Submitted?", "Grade", "URL"]
        ],
        use_container_width=True,
        hide_index=True,
        column_config={"URL": st.column_config.LinkColumn("Open in Canvas", display_text="Open")},
    )

st.subheader("All assignments")
st.caption("Filter and review everything Canvas returned for the selected classes.")

status_filter = st.multiselect(
    "Status filter",
    sorted(df["Status"].dropna().unique().tolist()),
    default=sorted(df["Status"].dropna().unique().tolist()),
)

all_df = df[df["Status"].isin(status_filter)].copy()
all_df = all_df.sort_values(["Due_dt", "Course", "Assignment"], na_position="last")

st.dataframe(
    all_df[
        [
            "Course", "Assignment", "Assigned / Available", "Due", "Status",
            "Submitted?", "Submitted at", "Late?", "Missing?", "Grade",
            "Score", "Points possible", "Percent", "URL",
        ]
    ],
    use_container_width=True,
    hide_index=True,
    column_config={"URL": st.column_config.LinkColumn("Canvas", display_text="Open")},
)

with st.expander("About the 'Assigned / Available' date"):
    st.write(
        "Canvas does not always provide a true 'assigned on' field. "
        "This dashboard uses the assignment's unlock/availability date when Canvas provides one; "
        "otherwise it falls back to the Canvas creation date."
    )

with st.expander("Privacy & refresh behavior"):
    st.write(
        "The token is kept only in this browser's active Streamlit session and is not saved to a file by the app. "
        "The dashboard automatically reruns about every 5 minutes while the tab is open. "
        "Canvas data is cached only inside that person's session for up to 5 minutes. "
        "The Refresh Canvas now button clears that session cache immediately."
    )
