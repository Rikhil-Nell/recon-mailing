"""
Recon 2026 — Sponsor Outreach Engine
A Streamlit app for generating personalized, research-backed sponsorship emails.
"""

import json
import os
from pathlib import Path

import streamlit as st
import pandas as pd
from dotenv import load_dotenv

from engine.data_loader import load_contacts, get_categories
from engine.research import research_company, get_cached_intel
from engine.email_generator import generate_email_sequence, get_cached_sequence

# ── Load .env ─────────────────────────────────────────────────────────────

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
JINA_API_KEY = os.getenv("JINA_API_KEY", "")

# ── Page Config ───────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Recon Outreach Engine",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

* { font-family: 'Inter', -apple-system, sans-serif; }

.stApp { background: #07070e; }

/* Sidebar */
section[data-testid="stSidebar"] > div {
    background: linear-gradient(180deg, #0c0c1d 0%, #111128 100%);
    border-right: 1px solid rgba(99, 102, 241, 0.15);
}

/* ── Stat Cards ── */
.stat-row {
    display: flex;
    gap: 10px;
    margin: 12px 0 20px 0;
}
.stat-card {
    flex: 1;
    background: linear-gradient(135deg, #12122a 0%, #1a1a3e 100%);
    border: 1px solid rgba(99, 102, 241, 0.2);
    border-radius: 12px;
    padding: 14px 10px;
    text-align: center;
}
.stat-number {
    font-size: 1.6rem;
    font-weight: 800;
    background: linear-gradient(135deg, #818cf8, #c084fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.stat-label {
    font-size: 0.65rem;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-top: 2px;
}

/* ── Company List Item ── */
.company-item {
    background: #0f0f23;
    border: 1px solid #1e1e3a;
    border-radius: 10px;
    padding: 14px 16px;
    margin: 6px 0;
    cursor: pointer;
    transition: all 0.2s ease;
}
.company-item:hover {
    border-color: #6366f1;
    background: #13132e;
    transform: translateX(2px);
}
.company-name {
    font-weight: 600;
    font-size: 0.95rem;
    color: #e2e8f0;
}
.company-meta {
    font-size: 0.75rem;
    color: #64748b;
    margin-top: 4px;
}

/* ── Status Badges ── */
.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.65rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.badge-not_started { background: #1e1e2e; color: #64748b; }
.badge-researched { background: #0f2a1f; color: #4ade80; border: 1px solid #166534; }
.badge-email_1_sent { background: #2a1f0f; color: #fbbf24; border: 1px solid #854d0e; }
.badge-follow_up_sent { background: #1f0f2a; color: #c084fc; border: 1px solid #6b21a8; }
.badge-replied { background: #0f1f2a; color: #60a5fa; border: 1px solid #1e40af; }
.badge-closed { background: #0f2a1a; color: #34d399; border: 1px solid #047857; }
.badge-declined { background: #2a0f0f; color: #f87171; border: 1px solid #991b1b; }

/* ── Detail Panel ── */
.detail-header {
    background: linear-gradient(135deg, #0f0f2d 0%, #1a1040 50%, #0f0f2d 100%);
    border: 1px solid rgba(99, 102, 241, 0.2);
    border-radius: 16px;
    padding: 28px 32px;
    margin-bottom: 24px;
}
.detail-title {
    font-size: 1.8rem;
    font-weight: 800;
    background: linear-gradient(135deg, #e2e8f0, #c084fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
}
.detail-category {
    font-size: 0.85rem;
    color: #818cf8;
    margin-top: 6px;
    font-weight: 500;
}

/* ── Contact Cards ── */
.contact-card {
    background: #0f0f23;
    border: 1px solid #1e1e3a;
    border-radius: 10px;
    padding: 12px 16px;
    margin: 6px 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.contact-name {
    font-weight: 600;
    color: #e2e8f0;
    font-size: 0.9rem;
}
.contact-email {
    color: #818cf8;
    font-size: 0.8rem;
    font-family: 'JetBrains Mono', monospace;
}
.contact-meta {
    font-size: 0.75rem;
    color: #64748b;
}

/* ── Intel Panel ── */
.intel-box {
    background: linear-gradient(135deg, #0a1628 0%, #0f1f35 100%);
    border: 1px solid rgba(56, 189, 248, 0.15);
    border-radius: 12px;
    padding: 20px 24px;
    margin: 8px 0;
}
.intel-label {
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #38bdf8;
    margin-bottom: 6px;
}
.intel-text {
    color: #cbd5e1;
    font-size: 0.88rem;
    line-height: 1.6;
}

/* ── Email Preview ── */
.email-card {
    background: #0c0c1a;
    border: 1px solid #1e1e3a;
    border-radius: 14px;
    padding: 24px 28px;
    margin: 12px 0;
}
.email-stage {
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 12px;
}
.email-stage-cold { color: #60a5fa; }
.email-stage-followup { color: #fbbf24; }
.email-stage-value { color: #34d399; }
.email-subject-line {
    font-size: 1.05rem;
    font-weight: 600;
    color: #e2e8f0;
    padding: 10px 14px;
    background: #111128;
    border-radius: 8px;
    border-left: 3px solid #6366f1;
    margin-bottom: 14px;
}
.email-body-text {
    color: #b0b8c8;
    font-size: 0.9rem;
    line-height: 1.75;
    white-space: pre-wrap;
    padding: 0 4px;
}

/* ── Dashboard Cards ── */
.dash-card {
    background: linear-gradient(135deg, #0f0f2d 0%, #151540 100%);
    border: 1px solid rgba(99, 102, 241, 0.15);
    border-radius: 14px;
    padding: 24px;
    text-align: center;
    height: 100%;
}
.dash-card h3 {
    font-size: 1rem;
    color: #c084fc;
    margin-bottom: 8px;
}
.dash-card p {
    font-size: 0.85rem;
    color: #94a3b8;
    line-height: 1.5;
}

/* ── Page Title ── */
.page-title {
    font-size: 2.2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #818cf8 0%, #c084fc 50%, #f0abfc 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 4px;
}
.page-subtitle {
    color: #64748b;
    font-size: 0.9rem;
    margin-bottom: 24px;
}

/* Hide streamlit defaults */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem; }
</style>
""", unsafe_allow_html=True)

# ── State Management ──────────────────────────────────────────────────────

STATUS_FILE = Path("cache/status.json")


def load_status_data() -> dict:
    if STATUS_FILE.exists():
        try:
            return json.loads(STATUS_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_status_data(data: dict) -> None:
    STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATUS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def get_company_status(company_name: str) -> str:
    return load_status_data().get(company_name, "not_started")


def set_company_status(company_name: str, status: str) -> None:
    statuses = load_status_data()
    statuses[company_name] = status
    save_status_data(statuses)


# ── Data Loading ──────────────────────────────────────────────────────────

@st.cache_data
def load_all_contacts():
    return load_contacts("data")


STATUS_LABELS = {
    "not_started": "⬜ Not Started",
    "researched": "🔬 Researched",
    "email_1_sent": "📨 Email 1 Sent",
    "follow_up_sent": "🔄 Follow-up Sent",
    "replied": "💬 Replied",
    "closed": "✅ Closed",
    "declined": "❌ Declined",
}

STATUS_KEYS = list(STATUS_LABELS.keys())


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  PAGES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def page_dashboard():
    """Home dashboard with stats and overview."""
    companies = load_all_contacts()
    statuses = load_status_data()

    st.markdown('<div class="page-title">Recon 2026 Outreach</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Sponsor outreach engine — research, personalize, convert.</div>', unsafe_allow_html=True)

    # ── Stats Row ──
    total = len(companies)
    total_contacts = sum(len(c.contacts) for c in companies.values())
    researched = sum(1 for c in companies if get_cached_intel(c) is not None)
    emailed = sum(1 for s in statuses.values() if s in ("email_1_sent", "follow_up_sent", "replied", "closed"))
    replied = sum(1 for s in statuses.values() if s == "replied")
    closed = sum(1 for s in statuses.values() if s == "closed")

    st.markdown(f"""
    <div class="stat-row">
        <div class="stat-card">
            <div class="stat-number">{total}</div>
            <div class="stat-label">Companies</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{total_contacts}</div>
            <div class="stat-label">Contacts</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{researched}</div>
            <div class="stat-label">Researched</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{emailed}</div>
            <div class="stat-label">Emailed</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{replied}</div>
            <div class="stat-label">Replied</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{closed}</div>
            <div class="stat-label">Closed</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── How it works ──
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="dash-card">
            <h3>📨 Step 1 — Cold Open</h3>
            <p>4-6 sentences. Lead with THEIR value. No bullet points. One clear ask. Get a reply, not a sale.</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="dash-card">
            <h3>🔄 Step 2 — Follow-Up</h3>
            <p>Send 4-5 days later. 2-3 sentences only. Add one new hook. Don't repeat the original pitch.</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="dash-card">
            <h3>💎 Step 3 — Value Drop</h3>
            <p>ONLY after they reply. Full pitch with tailored activations. Offer to share the sponsorship deck.</p>
        </div>
        """, unsafe_allow_html=True)

    # ── Category Breakdown ──
    st.markdown("---")
    st.markdown("#### 📊 Companies by Category")

    cat_counts = {}
    for c in companies.values():
        cat = c.category or "Uncategorized"
        cat_counts[cat] = cat_counts.get(cat, 0) + 1

    df = pd.DataFrame(
        [{"Category": k, "Companies": v} for k, v in sorted(cat_counts.items(), key=lambda x: -x[1])]
    )
    st.dataframe(df, use_container_width=True, hide_index=True)

    # ── Status Breakdown ──
    st.markdown("#### 📈 Outreach Pipeline")
    status_counts = {}
    for s in STATUS_KEYS:
        status_counts[STATUS_LABELS[s]] = sum(1 for v in statuses.values() if v == s)
    status_counts[STATUS_LABELS["not_started"]] = total - sum(status_counts.values()) + status_counts.get(STATUS_LABELS["not_started"], 0)

    sdf = pd.DataFrame([{"Stage": k, "Count": v} for k, v in status_counts.items() if v > 0])
    if not sdf.empty:
        st.dataframe(sdf, use_container_width=True, hide_index=True)


def page_companies():
    """Company browser + detail view."""
    companies = load_all_contacts()
    statuses = load_status_data()
    categories = ["All"] + get_categories(companies)

    st.markdown('<div class="page-title">Companies</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Browse, research, and generate personalized outreach.</div>', unsafe_allow_html=True)

    # ── Filters ──
    fcol1, fcol2, fcol3 = st.columns([2, 1, 1])
    with fcol1:
        search = st.text_input("🔎 Search", placeholder="Type a company name...", label_visibility="collapsed")
    with fcol2:
        cat_filter = st.selectbox("Category", categories, label_visibility="collapsed")
    with fcol3:
        status_filter = st.selectbox(
            "Status",
            ["All"] + STATUS_KEYS,
            format_func=lambda x: STATUS_LABELS.get(x, "All"),
            label_visibility="collapsed",
        )

    # ── Apply Filters ──
    filtered = {}
    for name, company in companies.items():
        if cat_filter != "All" and company.category != cat_filter:
            continue
        status = statuses.get(name, "not_started")
        if status_filter != "All" and status != status_filter:
            continue
        if search and search.lower() not in name.lower():
            continue
        filtered[name] = company

    # ── Layout: List + Detail ──
    col_list, col_detail = st.columns([1, 2], gap="large")

    with col_list:
        st.markdown(f"**{len(filtered)}** companies")

        for name in sorted(filtered.keys()):
            company = filtered[name]
            status = statuses.get(name, "not_started")
            has_research = get_cached_intel(name) is not None
            n_contacts = len(company.contacts)

            icons = "🟢" if has_research else "⚪"
            status_emoji = status.split("_")[0] if status != "not_started" else ""

            if st.button(
                f"{icons} {name}  ·  {n_contacts} contacts",
                key=f"btn_{name}",
                use_container_width=True,
            ):
                st.session_state["selected_company"] = name

    with col_detail:
        selected = st.session_state.get("selected_company")

        if selected and selected in companies:
            _render_company_detail(companies[selected])
        else:
            st.markdown("""
            <div style="text-align: center; padding: 80px 20px; color: #475569;">
                <div style="font-size: 3rem; margin-bottom: 16px;">🎯</div>
                <div style="font-size: 1.1rem; font-weight: 500;">Select a company from the list</div>
                <div style="font-size: 0.85rem; margin-top: 8px;">Click any company to view details, research, and generate emails.</div>
            </div>
            """, unsafe_allow_html=True)


def _render_company_detail(company):
    """Render detail panel for a selected company."""
    status = get_company_status(company.canonical_name)

    # ── Header ──
    st.markdown(f"""
    <div class="detail-header">
        <div class="detail-title">{company.canonical_name}</div>
        <div class="detail-category">{company.category}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Status ──
    new_status = st.selectbox(
        "Outreach Status",
        STATUS_KEYS,
        index=STATUS_KEYS.index(status),
        format_func=lambda x: STATUS_LABELS[x],
        key=f"status_{company.canonical_name}",
    )
    if new_status != status:
        set_company_status(company.canonical_name, new_status)
        st.rerun()

    # ── Contacts ──
    st.markdown("#### 👥 Contacts")
    for c in company.contacts:
        name_display = c.name if c.name else "—"
        cc = f"CC: {c.cc_name}" if c.cc_name else ""
        phone = f"📞 {c.phone}" if c.phone else ""
        meta_parts = [x for x in [cc, phone] if x]
        meta = " · ".join(meta_parts)

        st.markdown(f"""
        <div class="contact-card">
            <div>
                <div class="contact-name">{name_display}</div>
                <div class="contact-email">{c.email}</div>
            </div>
            <div class="contact-meta">{meta}</div>
        </div>
        """, unsafe_allow_html=True)

    # ── Research ──
    st.markdown("---")
    st.markdown("#### 🔬 Company Research")
    cached_intel = get_cached_intel(company.canonical_name)

    if cached_intel:
        _render_intel(cached_intel)
        if st.button("🔄 Re-research", key=f"refresh_{company.canonical_name}"):
            if not OPENAI_API_KEY:
                st.error("No OPENAI_API_KEY found in .env file!")
            else:
                with st.spinner("Re-researching..."):
                    research_company(company.canonical_name, company.category, OPENAI_API_KEY, JINA_API_KEY, force_refresh=True)
                    st.rerun()
    else:
        if st.button("🔍 Research this company", key=f"research_{company.canonical_name}", type="primary"):
            if not OPENAI_API_KEY:
                st.error("No OPENAI_API_KEY found in .env file!")
            else:
                with st.spinner(f"Researching {company.canonical_name}..."):
                    research_company(company.canonical_name, company.category, OPENAI_API_KEY, JINA_API_KEY)
                    st.rerun()

    # ── Emails ──
    st.markdown("---")
    st.markdown("#### ✉️ Email Sequences")

    if not cached_intel:
        st.info("Research the company first to unlock email generation.")
        return

    contact_options = [c for c in company.contacts if c.email]
    if not contact_options:
        st.warning("No contacts with email addresses.")
        return

    selected_contact = st.selectbox(
        "Generate for:",
        contact_options,
        format_func=lambda c: f"{c.name or '—'} · {c.email}" + (f" (CC: {c.cc_name})" if c.cc_name else ""),
        key=f"contact_{company.canonical_name}",
    )

    cached_seq = get_cached_sequence(company.canonical_name, selected_contact.email)

    if cached_seq:
        _render_email_sequence(cached_seq)
        if st.button("🔄 Regenerate", key=f"regen_{company.canonical_name}_{selected_contact.email}"):
            if not OPENAI_API_KEY:
                st.error("No OPENAI_API_KEY found in .env file!")
            else:
                with st.spinner("Regenerating..."):
                    generate_email_sequence(cached_intel, selected_contact, OPENAI_API_KEY, force_refresh=True)
                    st.rerun()
    else:
        if st.button("⚡ Generate Email Sequence", key=f"gen_{company.canonical_name}_{selected_contact.email}", type="primary"):
            if not OPENAI_API_KEY:
                st.error("No OPENAI_API_KEY found in .env file!")
            else:
                with st.spinner("Generating 3-email sequence..."):
                    generate_email_sequence(cached_intel, selected_contact, OPENAI_API_KEY)
                    st.rerun()


def _render_intel(intel):
    """Render company research intel cards."""
    fields = [
        ("🌐 What They Do", intel.summary),
        ("🔒 Security Relevance", intel.security_relevance),
        ("🎓 Campus / Dev Programs", intel.campus_programs),
        ("📰 Recent Activity", intel.recent_news),
        ("🎯 Suggested Angle", intel.suggested_angle),
    ]
    for label, text in fields:
        st.markdown(f"""
        <div class="intel-box">
            <div class="intel-label">{label}</div>
            <div class="intel-text">{text}</div>
        </div>
        """, unsafe_allow_html=True)


def _render_email_sequence(seq):
    """Render the 3-email sequence as tabs."""
    stage_config = {
        "cold_open": ("📨 Cold Open", "email-stage-cold"),
        "follow_up": ("🔄 Follow-Up", "email-stage-followup"),
        "value_drop": ("💎 Value Drop", "email-stage-value"),
    }

    tabs = st.tabs([stage_config.get(e.stage, (e.stage, ""))[0] for e in seq.emails])

    for tab, email in zip(tabs, seq.emails):
        with tab:
            stage_label, stage_class = stage_config.get(email.stage, (email.stage, ""))

            st.markdown(f"""
            <div class="email-card">
                <div class="email-stage {stage_class}">{stage_label}</div>
                <div class="email-subject-line">{email.subject}</div>
                <div class="email-body-text">{email.body}</div>
            </div>
            """, unsafe_allow_html=True)

            # Copyable fields
            with st.expander("📋 Copy Subject & Body"):
                st.code(email.subject, language=None)
                st.code(email.body, language=None)


def page_tracker():
    """Pipeline tracker view — see all companies and their statuses at a glance."""
    companies = load_all_contacts()
    statuses = load_status_data()

    st.markdown('<div class="page-title">Pipeline Tracker</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Full outreach status at a glance.</div>', unsafe_allow_html=True)

    # Build table data
    rows = []
    for name in sorted(companies.keys()):
        company = companies[name]
        status = statuses.get(name, "not_started")
        has_research = get_cached_intel(name) is not None
        n_contacts = len(company.contacts)
        emails_list = [c.email for c in company.contacts if c.email]
        primary_email = emails_list[0] if emails_list else "—"
        cc_names = set(c.cc_name for c in company.contacts if c.cc_name)

        rows.append({
            "Company": name,
            "Category": company.category,
            "Contacts": n_contacts,
            "Primary Email": primary_email,
            "CC Owners": ", ".join(sorted(cc_names)) if cc_names else "—",
            "Researched": "✅" if has_research else "❌",
            "Status": STATUS_LABELS.get(status, status),
        })

    df = pd.DataFrame(rows)

    # Filters on top
    fcol1, fcol2 = st.columns(2)
    with fcol1:
        tracker_cat = st.multiselect(
            "Filter by category",
            options=sorted(df["Category"].unique()),
            default=[],
        )
    with fcol2:
        tracker_status = st.multiselect(
            "Filter by status",
            options=sorted(df["Status"].unique()),
            default=[],
        )

    if tracker_cat:
        df = df[df["Category"].isin(tracker_cat)]
    if tracker_status:
        df = df[df["Status"].isin(tracker_status)]

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        height=600,
        column_config={
            "Company": st.column_config.TextColumn("Company", width="medium"),
            "Category": st.column_config.TextColumn("Category", width="medium"),
            "Primary Email": st.column_config.TextColumn("Primary Email", width="large"),
        },
    )

    # Export
    st.markdown("---")
    csv_data = df.to_csv(index=False)
    st.download_button(
        "📥 Export to CSV",
        csv_data,
        "recon_outreach_tracker.csv",
        "text/csv",
    )


def page_batch():
    """Batch operations — research or generate emails for multiple companies at once."""
    companies = load_all_contacts()

    st.markdown('<div class="page-title">Batch Operations</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Research or generate emails for multiple companies at once.</div>', unsafe_allow_html=True)

    if not OPENAI_API_KEY:
        st.error("⚠️ No OPENAI_API_KEY found in your `.env` file. Add it and restart the app.")
        return

    categories = get_categories(companies)

    st.markdown("#### 🔬 Batch Research")
    st.markdown("Research all un-researched companies in a category.")

    batch_cat = st.selectbox("Category to batch research", ["All"] + categories, key="batch_cat")

    # Count unresearched
    targets = []
    for name, company in sorted(companies.items()):
        if batch_cat != "All" and company.category != batch_cat:
            continue
        if get_cached_intel(name) is None:
            targets.append((name, company))

    st.markdown(f"**{len(targets)}** companies need research" + (f" in {batch_cat}" if batch_cat != "All" else ""))

    if targets and st.button(f"🚀 Research {len(targets)} companies", type="primary"):
        progress = st.progress(0)
        status_text = st.empty()

        for i, (name, company) in enumerate(targets):
            status_text.markdown(f"Researching **{name}**... ({i+1}/{len(targets)})")
            try:
                research_company(name, company.category, OPENAI_API_KEY, JINA_API_KEY)
            except Exception as e:
                st.warning(f"Failed for {name}: {e}")
            progress.progress((i + 1) / len(targets))

        status_text.markdown("✅ **Batch research complete!**")
        st.balloons()

    st.markdown("---")
    st.markdown("#### ✉️ Batch Email Generation")
    st.markdown("Generate emails for all researched companies that don't have sequences yet.")

    email_cat = st.selectbox("Category to batch generate", ["All"] + categories, key="email_cat")

    email_targets = []
    for name, company in sorted(companies.items()):
        if email_cat != "All" and company.category != email_cat:
            continue
        intel = get_cached_intel(name)
        if intel is None:
            continue
        # Check if ANY contact has a cached sequence
        has_any = any(get_cached_sequence(name, c.email) is not None for c in company.contacts if c.email)
        if not has_any:
            # Pick first contact with email
            first_contact = next((c for c in company.contacts if c.email), None)
            if first_contact:
                email_targets.append((name, company, intel, first_contact))

    st.markdown(f"**{len(email_targets)}** companies ready for email generation" + (f" in {email_cat}" if email_cat != "All" else ""))

    if email_targets and st.button(f"⚡ Generate for {len(email_targets)} companies", type="primary"):
        progress = st.progress(0)
        status_text = st.empty()

        for i, (name, company, intel, contact) in enumerate(email_targets):
            status_text.markdown(f"Generating emails for **{name}** → {contact.email}... ({i+1}/{len(email_targets)})")
            try:
                generate_email_sequence(intel, contact, OPENAI_API_KEY)
            except Exception as e:
                st.warning(f"Failed for {name}: {e}")
            progress.progress((i + 1) / len(email_targets))

        status_text.markdown("✅ **Batch email generation complete!**")
        st.balloons()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  MAIN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def main():
    # ── Sidebar Navigation ──
    with st.sidebar:
        st.markdown("## 🎯 Recon Engine")
        st.markdown("*v1.0 — Outreach Toolkit*")
        st.markdown("---")

        page = st.radio(
            "Navigate",
            ["🏠 Dashboard", "🏢 Companies", "📊 Tracker", "🚀 Batch Ops"],
            label_visibility="collapsed",
        )

        st.markdown("---")

        # API status indicators
        st.markdown("##### 🔌 Connections")
        if OPENAI_API_KEY:
            st.markdown(f'<span class="badge badge-researched">OpenAI ✓</span>', unsafe_allow_html=True)
        else:
            st.markdown(f'<span class="badge badge-declined">OpenAI ✗</span>', unsafe_allow_html=True)

        if JINA_API_KEY:
            st.markdown(f'<span class="badge badge-researched">Jina ✓</span>', unsafe_allow_html=True)
        else:
            st.markdown(f'<span class="badge badge-not_started">Jina (optional)</span>', unsafe_allow_html=True)

        st.markdown("---")
        st.markdown(
            '<div style="font-size: 0.7rem; color: #475569; text-align: center;">'
            'OSC × Null Chapter · VIT-AP'
            '</div>',
            unsafe_allow_html=True,
        )

    # ── Route to page ──
    try:
        load_all_contacts()
    except FileNotFoundError:
        st.error("📁 `data/BD 25.2.csv` not found! Place the CSV in the `data/` folder.")
        return

    if page == "🏠 Dashboard":
        page_dashboard()
    elif page == "🏢 Companies":
        page_companies()
    elif page == "📊 Tracker":
        page_tracker()
    elif page == "🚀 Batch Ops":
        page_batch()


if __name__ == "__main__":
    main()
