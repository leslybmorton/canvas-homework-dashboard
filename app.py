import os
import time
import json
import html
from datetime import datetime
from zoneinfo import ZoneInfo
from urllib.parse import urlparse

import pandas as pd
import requests
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from streamlit_cookies_manager import EncryptedCookieManager

st.set_page_config(
    page_title="Canvas Homework Dashboard",
    page_icon="📚",
    layout="wide",
)


# Optional encrypted "Remember me" cookie.
# On Streamlit Community Cloud, set COOKIES_PASSWORD in App settings > Secrets.
try:
    COOKIE_PASSWORD = st.secrets.get("COOKIES_PASSWORD", "")
except Exception:
    COOKIE_PASSWORD = os.getenv("COOKIES_PASSWORD", "")

cookies = None
REMEMBER_ME_AVAILABLE = bool(COOKIE_PASSWORD)
if REMEMBER_ME_AVAILABLE:
    cookies = EncryptedCookieManager(
        prefix="canvas-homework-dashboard/",
        password=COOKIE_PASSWORD,
    )
    if not cookies.ready():
        st.stop()

REMEMBER_COOKIE_KEY = "canvas_connection"


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

if "suppress_cookie_restore" not in st.session_state:
    st.session_state.suppress_cookie_restore = False

def save_remembered_connection(base_url, token, timezone):
    if not REMEMBER_ME_AVAILABLE or cookies is None:
        return
    cookies[REMEMBER_COOKIE_KEY] = json.dumps({
        "base_url": base_url,
        "token": token,
        "timezone": timezone,
    })
    cookies.save()

def forget_remembered_connection():
    if not REMEMBER_ME_AVAILABLE or cookies is None:
        return
    try:
        if REMEMBER_COOKIE_KEY in cookies:
            del cookies[REMEMBER_COOKIE_KEY]
            cookies.save()
    except Exception:
        pass

# Restore the connection from this device's encrypted browser cookie.
if (
    REMEMBER_ME_AVAILABLE
    and cookies is not None
    and not st.session_state.connected
    and not st.session_state.suppress_cookie_restore
):
    remembered = cookies.get(REMEMBER_COOKIE_KEY)
    if remembered:
        try:
            saved = json.loads(remembered)
            saved_url = (saved.get("base_url") or "").strip()
            saved_token = (saved.get("token") or "").strip()
            saved_timezone = (saved.get("timezone") or DEFAULT_TZ).strip()
            if saved_url and saved_token:
                st.session_state.canvas_base_url = saved_url
                st.session_state.canvas_token = saved_token
                st.session_state.canvas_timezone = saved_timezone
                st.session_state.connected = True
        except Exception:
            forget_remembered_connection()


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
    elif submitted and sub.get("grade") is not None:
        status = "Graded"
    elif submitted:
        status = "Submitted"
    elif not actionable and due:
        status = "No Canvas submission"
    # Canvas can sometimes flag an unsubmitted assignment as "missing"
    # even when its due date is still in the future. For this dashboard,
    # "Missing" means the due date has actually passed.
    elif due and due < now and missing:
        status = "Missing"
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
        "Missing?": "Yes" if (missing and due and due < now) else "No",
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




st.markdown(
    """
    <style>
    /* Parent dashboard redesign */
    .block-container {max-width: 1500px; padding-top: 1.4rem; padding-bottom: 3rem;}
    #MainMenu {visibility:hidden;}
    footer {visibility:hidden;}

    .compact-hero {margin-bottom:.4rem !important;}
    .refresh-pill {
        display:inline-block; float:right; margin-top:-.25rem; margin-bottom:1rem;
        background:#E8F1F3; color:#2F6673; border:1px solid #D7E5E8;
        border-radius:999px; padding:.35rem .8rem; font-size:.82rem; font-weight:650;
    }

    .side-card {
        background:#FFFDF9; border:1px solid rgba(60,87,99,.18);
        border-radius:14px; padding:.9rem; margin:.7rem 0;
        box-shadow:0 3px 10px rgba(61,52,47,.04);
    }
    .connected-title {color:#3C7C58; font-weight:750; margin-bottom:.35rem;}
    .connected-name {font-weight:700; color:#3D342F;}
    .connected-sub {font-size:.78rem; color:#7A6F68; margin-top:.2rem;}
    .tip-card {font-size:.85rem; line-height:1.45;}

    .summary-grid {
        display:grid; grid-template-columns:repeat(4,1fr); gap:16px;
        clear:both; margin:1.3rem 0 1rem;
    }
    .summary-card {
        background:#FFFDF9; border:1px solid rgba(60,87,99,.14); border-radius:18px;
        padding:1rem 1.05rem; display:flex; gap:.9rem; align-items:center;
        box-shadow:0 5px 15px rgba(61,52,47,.055);
    }
    .summary-card .summary-icon {
        width:48px; height:48px; border-radius:50%; display:flex; align-items:center;
        justify-content:center; font-size:1.45rem; font-weight:800; flex:0 0 auto;
    }
    .summary-card span {display:block; font-size:.9rem; font-weight:700; color:#3D4E58;}
    .summary-card strong {display:block; font-size:2rem; line-height:1.05; margin:.18rem 0;}
    .summary-card small {display:block; color:#766B64;}
    .coral .summary-icon {background:#FCE7DF; color:#D85A3B;} .coral strong{color:#D85A3B;}
    .gold .summary-icon {background:#FBF0D8; color:#C88A28;} .gold strong{color:#C88A28;}
    .green .summary-icon {background:#E5F1E6; color:#4C9463;} .green strong{color:#4C9463;}
    .blue .summary-icon {background:#E5EEF7; color:#3E78AC;} .blue strong{color:#3E78AC;}

    .priority-shell {
        background:#FFFDF9; border:1px solid rgba(60,87,99,.14); border-radius:16px 16px 0 0;
        overflow:hidden; box-shadow:0 5px 15px rgba(61,52,47,.05);
        margin-bottom:0;
    }
    .priority-title {font-size:1rem; font-weight:800; padding:.9rem 1rem; border-bottom:1px solid #EEE7DF;}
    .coral-line {border-left:4px solid #E36B4D;} .coral-line .priority-title{color:#C9482B;}
    .gold-line {border-left:4px solid #D9A03B;} .gold-line .priority-title{color:#B77B17;}
    .green-line {border-left:4px solid #65A979;} .green-line .priority-title{color:#3F8053;}
    .blue-line {border-left:4px solid #4E87BB;} .blue-line .priority-title{color:#2E6B9F;}
    .priority-body {
        padding:0 .9rem; background:#FFFDF9;
        border-left:1px solid rgba(60,87,99,.14);
        border-right:1px solid rgba(60,87,99,.14);
    }
    .assignment-link {display:block; text-decoration:none !important; color:inherit !important; border-radius:10px;}
    .assignment-link:hover {background:#F5F1EB; transform:translateY(-1px);}
    .assignment-link:hover .assignment-name {color:#2F6E7C !important;}
    .assignment-item {display:flex; justify-content:space-between; gap:.5rem; padding:.85rem .35rem; border-bottom:1px solid #EFE8E1; transition:background .15s ease, transform .15s ease;}
    .assignment-copy {min-width:0;}
    .course-name {font-size:.76rem; color:#6F6964; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;}
    .assignment-name {font-size:.9rem; font-weight:750; color:#283B46; margin:.14rem 0; line-height:1.25;}
    .due-line {font-size:.76rem; color:#756B65;}
    .status-badge {align-self:center; flex:0 0 auto; border-radius:7px; padding:.22rem .42rem; font-size:.7rem; font-weight:700;}
    .badge-missing {background:#FDE9E3; color:#C94C2E; border:1px solid #F5C8BB;}
    .badge-today {background:#FBF1DE; color:#A96E12; border:1px solid #EED8AC;}
    .badge-tomorrow {background:#E8F3E9; color:#3F8053; border:1px solid #CDE4D1;}
    .badge-upcoming {background:#E8F0F7; color:#316E9E; border:1px solid #CDDFEE;}
    .more-line {padding:.7rem 1rem; color:#2F6E7C; font-size:.78rem; font-weight:700;}
    .empty-state {padding:1.1rem .1rem; color:#7C746E; font-size:.85rem;}

    .privacy-footer {text-align:center; color:#716A64; font-size:.82rem; padding:1rem 0;}

    /* Keep connected-page Streamlit controls light */
    section[data-testid="stSidebar"] {background:#EAF1F2 !important;}
    div[data-testid="stDataFrame"] {background:#FFFDF9 !important; border-radius:14px; overflow:hidden;}
    div[data-testid="stTextInput"] input {background:#FFFDF9 !important; color:#3D342F !important;}
    div[data-testid="stSelectbox"] > div > div,
    div[data-testid="stMultiSelect"] > div > div {background:#FFFDF9 !important; color:#3D342F !important;}

    @media (max-width: 1000px) {
        .summary-grid {grid-template-columns:repeat(2,1fr);}
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ----------------------------
# Public landing / connection
# ----------------------------
if not st.session_state.connected:
    st.markdown(
        """
        <div class="dashboard-hero">
            <h1>📚 Canvas Homework Dashboard</h1>
            <p>See what's missing, what's due soon, and what's coming up — without digging through every class.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="instruction-card">
            <span class="soft-badge">Private session</span>
            <span class="soft-badge">5-minute refresh</span>
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

    remember_me = st.checkbox(
        "Remember me on this device",
        value=True,
        disabled=not REMEMBER_ME_AVAILABLE,
        help=(
            "Stores the Canvas connection in an encrypted browser cookie on this device."
            if REMEMBER_ME_AVAILABLE
            else "The app owner needs to enable encrypted remembered logins in Streamlit settings."
        ),
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
            get_profile()
            st.session_state.connected = True
            st.session_state.suppress_cookie_restore = False
            if remember_me:
                save_remembered_connection(
                    normalized,
                    token.strip(),
                    timezone,
                )
            st.rerun()
        except Exception as e:
            st.session_state.canvas_token = ""
            st.session_state.connected = False
            clear_session_cache()
            st.error(f"Could not connect: {e}")

    st.stop()


# Automatically rerun every 5 minutes while the tab is open.
st_autorefresh(interval=CACHE_TTL_SECONDS * 1000, key="canvas_auto_refresh")

try:
    profile = get_profile()
except Exception as e:
    st.error(str(e))
    st.session_state.connected = False
    st.stop()

display_name = profile.get("short_name") or profile.get("name") or "Canvas student"

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("## 📚 Canvas Homework")
    st.caption("See what's missing, what's due soon, and what's coming up.")

    st.markdown(
        f"""
        <div class="side-card connected-card">
            <div class="connected-title">● &nbsp; Connected</div>
            <div class="connected-name">{display_name}</div>
            <div class="connected-sub">Auto-refresh: every 5 minutes</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("↻ Refresh now", use_container_width=True):
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
    st.markdown("### Courses")
    course_names = [c["name"] for c in courses]
    selected_names = st.multiselect(
        "Show",
        course_names,
        default=course_names,
        label_visibility="collapsed",
    )

    st.markdown("### Display")
    show_no_due = st.checkbox("Include assignments with no due date", value=False)
    show_no_canvas_submission = st.checkbox("Include 'No Canvas submission' items", value=True)

    st.markdown(
        """
        <div class="side-card tip-card">
            <b>💡 Tip</b><br>
            <span>Use “Open” on any assignment to jump directly into Canvas.</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Disconnect for now", use_container_width=True):
        st.session_state.canvas_token = ""
        st.session_state.canvas_base_url = ""
        st.session_state.connected = False
        st.session_state.suppress_cookie_restore = True
        clear_session_cache()
        st.rerun()

    if REMEMBER_ME_AVAILABLE and cookies is not None and cookies.get(REMEMBER_COOKIE_KEY):
        if st.button("Forget this device", use_container_width=True):
            forget_remembered_connection()
            st.session_state.canvas_token = ""
            st.session_state.canvas_base_url = ""
            st.session_state.connected = False
            st.session_state.suppress_cookie_restore = True
            clear_session_cache()
            st.rerun()

selected_courses = [c for c in courses if c["name"] in selected_names]

rows = []
now = datetime.now(ZoneInfo(st.session_state.canvas_timezone))

with st.spinner("Loading assignments…"):
    for course in selected_courses:
        try:
            assignments = get_assignments(course["id"])
            for a in assignments:
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

# Recalculate the parent-facing status from the actual due date.
# This deliberately overrides Canvas's premature `missing` flag for future work.
tomorrow = (now + pd.Timedelta(days=1)).date()
df["Dashboard status"] = df["Status"]

future_unsubmitted = (~df["_submitted"]) & df["Due_dt"].notna() & (df["Due_dt"] >= now)

# Anything Canvas calls Missing/Overdue cannot remain in that bucket if its due date
# is still in the future.
df.loc[future_unsubmitted, "Dashboard status"] = "Upcoming"

df.loc[
    future_unsubmitted
    & (df["Due_dt"].apply(lambda x: x.date() if x is not None else None) == now.date()),
    "Dashboard status",
] = "Due today"

df.loc[
    future_unsubmitted
    & (df["Due_dt"].apply(lambda x: x.date() if x is not None else None) == tomorrow),
    "Dashboard status",
] = "Due tomorrow"

# Missing/Overdue is reserved for genuinely past-due, unsubmitted work.
past_unsubmitted = (~df["_submitted"]) & df["Due_dt"].notna() & (df["Due_dt"] < now)
df.loc[
    past_unsubmitted & df["_missing"],
    "Dashboard status",
] = "Missing"
df.loc[
    past_unsubmitted & (~df["_missing"]),
    "Dashboard status",
] = "Overdue"

# ---------- Main header ----------
st.markdown(
    """
    <div class="dashboard-hero compact-hero">
        <h1>Canvas Homework Dashboard</h1>
        <p>Your Canvas assignments, prioritized so the important stuff is easy to spot.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="refresh-pill">Parent UI 2.5 · Auto-refresh: every 5 minutes</div>',
    unsafe_allow_html=True,
)

active = df[(~df["_submitted"]) & df["Due_dt"].notna()].copy()
missing_count = int(active["Dashboard status"].isin(["Missing", "Overdue"]).sum())
today_count = int((active["Dashboard status"] == "Due today").sum())
tomorrow_count = int((active["Dashboard status"] == "Due tomorrow").sum())

end_of_today = now.replace(hour=23, minute=59, second=59)
seven_day_cutoff = end_of_today + pd.Timedelta(days=7)
upcoming_count = int(
    (
        active["Due_dt"].notna()
        & (active["Due_dt"] > end_of_today + pd.Timedelta(days=1))
        & (active["Due_dt"] <= seven_day_cutoff)
    ).sum()
)

# Summary cards
st.markdown(
    f"""
    <div class="summary-grid">
      <div class="summary-card coral"><div class="summary-icon">!</div><div><span>Missing / Overdue</span><strong>{missing_count}</strong><small>Needs attention</small></div></div>
      <div class="summary-card gold"><div class="summary-icon">▣</div><div><span>Due Today</span><strong>{today_count}</strong><small>Due by 11:59 PM</small></div></div>
      <div class="summary-card green"><div class="summary-icon">▣</div><div><span>Due Tomorrow</span><strong>{tomorrow_count}</strong><small>Tomorrow</small></div></div>
      <div class="summary-card blue"><div class="summary-icon">▣</div><div><span>Upcoming (Next 7 Days)</span><strong>{upcoming_count}</strong><small>After tomorrow</small></div></div>
    </div>
    """,
    unsafe_allow_html=True,
)

def due_text(row):
    return row["Due"] if row["Due"] != "—" else "No due date"

def assignment_items_html(rows_df, limit=None):
    shown = rows_df if limit is None else rows_df.head(limit)
    if shown.empty:
        return '<div class="empty-state">Nothing here 🎉</div>'

    parts = []
    for _, r in shown.iterrows():
        status = r["Dashboard status"]
        badge_class = {
            "Missing": "badge-missing",
            "Overdue": "badge-missing",
            "Due today": "badge-today",
            "Due tomorrow": "badge-tomorrow",
            "Upcoming": "badge-upcoming",
        }.get(status, "badge-upcoming")

        url = html.escape(str(r.get("URL") or ""), quote=True)
        course = html.escape(str(r["Course"]))
        assignment = html.escape(str(r["Assignment"]))
        due = html.escape(str(due_text(r)))
        safe_status = html.escape(str(status))

        card = f"""
        <div class="assignment-item">
            <div class="assignment-copy">
                <div class="course-name">{course}</div>
                <div class="assignment-name">{assignment}</div>
                <div class="due-line">Due {due}</div>
            </div>
            <span class="status-badge {badge_class}">{safe_status}</span>
        </div>
        """
        if url:
            card = f'<a class="assignment-link" href="{url}" target="_blank" rel="noopener noreferrer">{card}</a>'
        parts.append(card)
    return "".join(parts)

def render_priority_panel(title, rows_df, css_class, empty_message, state_key, limit=4):
    expanded = st.session_state.get(state_key, False)
    shown = rows_df if expanded else rows_df.head(limit)

    st.markdown(
        f'<div class="priority-shell {css_class}"><div class="priority-title">{title}</div></div>',
        unsafe_allow_html=True,
    )

    if rows_df.empty:
        st.markdown(f'<div class="empty-state">{empty_message}</div>', unsafe_allow_html=True)
    else:
        st.html(f'<div class="priority-body">{assignment_items_html(shown)}</div>')

    remaining = max(0, len(rows_df) - limit)
    if remaining > 0:
        label = "Show less" if expanded else f"+ {remaining} more"
        if st.button(label, key=f"{state_key}_button", use_container_width=True):
            st.session_state[state_key] = not expanded
            st.rerun()

missing_df = active[active["Dashboard status"].isin(["Missing", "Overdue"])].sort_values(
    ["Due_dt", "Course", "Assignment"]
)
today_df = active[active["Dashboard status"] == "Due today"].sort_values(
    ["Due_dt", "Course", "Assignment"]
)
tomorrow_df = active[active["Dashboard status"] == "Due tomorrow"].sort_values(
    ["Due_dt", "Course", "Assignment"]
)
upcoming_df = active[
    active["Due_dt"].notna()
    & (active["Due_dt"] > end_of_today + pd.Timedelta(days=1))
    & (active["Due_dt"] <= seven_day_cutoff)
].sort_values(["Due_dt", "Course", "Assignment"])

c1, c2, c3, c4 = st.columns(4, gap="small")
with c1:
    render_priority_panel("Missing / Overdue", missing_df, "coral-line", "Nothing missing 🎉", "expand_missing")
with c2:
    render_priority_panel("Due Today", today_df, "gold-line", "Nothing due today", "expand_today")
with c3:
    render_priority_panel("Due Tomorrow", tomorrow_df, "green-line", "Nothing due tomorrow", "expand_tomorrow")
with c4:
    render_priority_panel("Upcoming (Next 7 Days)", upcoming_df, "blue-line", "Nothing upcoming", "expand_upcoming")

# ---------- All assignments ----------
st.markdown("## All Assignments")
st.caption("Search, filter, and review everything Canvas returned for the selected classes.")

f1, f2 = st.columns([2, 1])
with f1:
    search_term = st.text_input(
        "Search assignments",
        placeholder="Search course or assignment…",
        label_visibility="collapsed",
    )
with f2:
    status_options = sorted(df["Dashboard status"].dropna().unique().tolist())
    selected_statuses = st.multiselect(
        "Filter status",
        status_options,
        default=status_options,
        label_visibility="collapsed",
        placeholder="Filter status",
    )

all_df = df[df["Dashboard status"].isin(selected_statuses)].copy()
if search_term.strip():
    q = search_term.strip().lower()
    all_df = all_df[
        all_df["Course"].str.lower().str.contains(q, na=False)
        | all_df["Assignment"].str.lower().str.contains(q, na=False)
    ]

all_df = all_df.sort_values(["Due_dt", "Course", "Assignment"], na_position="last")

table_df = all_df[
    [
        "Course", "Assignment", "Due", "Dashboard status",
        "Submitted?", "Grade", "Score", "Points possible", "Percent", "URL",
    ]
].rename(columns={
    "Dashboard status": "Status",
    "Points possible": "Points",
})

st.dataframe(
    table_df,
    use_container_width=True,
    hide_index=True,
    height=420,
    column_config={
        "Course": st.column_config.TextColumn("Course", width="medium"),
        "Assignment": st.column_config.TextColumn("Assignment", width="large"),
        "Due": st.column_config.TextColumn("Due", width="medium"),
        "Status": st.column_config.TextColumn("Status", width="small"),
        "Submitted?": st.column_config.TextColumn("Submitted?", width="small"),
        "Grade": st.column_config.TextColumn("Grade", width="small"),
        "Score": st.column_config.TextColumn("Score", width="small"),
        "Points": st.column_config.TextColumn("Points", width="small"),
        "Percent": st.column_config.TextColumn("Percent", width="small"),
        "URL": st.column_config.LinkColumn("Open in Canvas", display_text="Open"),
    },
)

st.markdown(
    """
    <div class="privacy-footer">🔒 If “Remember me” is enabled, your Canvas connection is stored only in an encrypted cookie on this device. Otherwise it is session-only.</div>
    """,
    unsafe_allow_html=True,
)

with st.expander("About the 'Assigned / Available' date"):
    st.write(
        "Canvas does not always provide a true 'assigned on' field. "
        "This dashboard uses the assignment's unlock/availability date when Canvas provides one; "
        "otherwise it falls back to the Canvas creation date."
    )
