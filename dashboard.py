

import streamlit as st
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go


st.set_page_config(
    page_title="SDA UP – Metadata Registry Dashboard",
    page_icon="🗂️",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown("""
<style>
    /* Main background */
    .main { background-color: #f5f7fa; }

    /* Metric cards */
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e0e4ea;
        border-radius: 10px;
        padding: 16px 20px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.06);
    }
    div[data-testid="metric-container"] label {
        font-size: 0.78rem;
        color: #6b7280;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Section headers */
    .section-header {
        background: linear-gradient(90deg, #1e3a5f 0%, #2563eb 100%);
        color: white;
        padding: 10px 18px;
        border-radius: 8px;
        font-size: 1.05rem;
        font-weight: 700;
        margin-bottom: 14px;
        margin-top: 10px;
    }

    /* Non-compliant highlight */
    .red-badge {
        background: #fee2e2;
        color: #991b1b;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: 600;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #1e3a5f;
    }
    section[data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }
</style>
""", unsafe_allow_html=True)


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROC_DIR = os.path.join(BASE_DIR, "data", "processed")
META_FILE    = os.path.join(BASE_DIR, "data", "metadata_submissions.csv")
TRACKER_FILE = os.path.join(BASE_DIR, "data", "compliance_tracker.csv")
FLAGS_FILE   = os.path.join(PROC_DIR, "quality_flags.csv")
REPORT_FILE  = os.path.join(PROC_DIR, "compliance_report.csv")
DPDP_FILE    = os.path.join(PROC_DIR, "dpdp_detail.csv")


@st.cache_data
def load_data():
    meta    = pd.read_csv(META_FILE,    dtype=str).fillna("")
    tracker = pd.read_csv(TRACKER_FILE, dtype=str).fillna("")
    tracker["final_status"] = tracker["final_status"].str.strip()
    flags   = pd.read_csv(FLAGS_FILE,   dtype=str).fillna("")
    report  = pd.read_csv(REPORT_FILE,  dtype=str).fillna("")
    dpdp    = pd.read_csv(DPDP_FILE,    dtype=str).fillna("")
    return meta, tracker, flags, report, dpdp


meta, tracker, flags, report, dpdp = load_data()

# ── sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🗂️ SDA Metadata Registry")
    st.markdown("**State Data Authority – Uttar Pradesh**")
    st.markdown("---")
    st.markdown("**Report Date:** 25 April 2026")
    st.markdown("**Batch:** April 2026")
    st.markdown("---")
    view = st.radio(
        "Navigate to panel:",
        ["📊 Overview", "🏛️ Department Status",
         "⚠️ Issue Breakdown", "🔒 DPDP Flag Tracker"],
    )
    st.markdown("---")
    st.caption("Data loads from /data/processed/ CSVs")


if view == "📊 Overview":
    st.markdown('<div class="section-header">📊 Panel 1 — Registry Overview</div>',
                unsafe_allow_html=True)

    total      = len(meta)
    approved   = len(tracker[tracker["final_status"] == "Approved"])
    pending    = len(tracker[tracker["final_status"].str.startswith("Pending")])
    dpdp_issue = len(dpdp[dpdp["fully_compliant"] != "Yes"])

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Submissions", total)
    c2.metric("Approved", f"{approved}  ({round(100*approved/total)}%)",
              delta=f"+{approved} approved", delta_color="normal")
    c3.metric("Pending Correction", f"{pending}  ({round(100*pending/total)}%)",
              delta=f"{pending} need action", delta_color="inverse")
    c4.metric("DPDP Issues", dpdp_issue,
              delta="datasets non-compliant", delta_color="inverse")

    st.markdown("---")

    # Donut: approval breakdown
    col_a, col_b = st.columns([1, 1])

    with col_a:
        st.subheader("Approval Status Breakdown")
        fig_donut = go.Figure(go.Pie(
            labels=["Approved", "Pending"],
            values=[approved, pending],
            hole=0.55,
            marker_colors=["#22c55e", "#f97316"],
            textinfo="label+percent",
            hovertemplate="%{label}: %{value}<extra></extra>",
        ))
        fig_donut.update_layout(
            showlegend=True,
            margin=dict(t=20, b=20, l=20, r=20),
            height=300,
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    with col_b:
        st.subheader("Submissions by Sector")
        sector_counts = meta.groupby("sector").size().reset_index(name="count")
        fig_bar = px.bar(
            sector_counts.sort_values("count", ascending=True),
            x="count", y="sector", orientation="h",
            color="count",
            color_continuous_scale="Blues",
            labels={"count": "# Datasets", "sector": "Sector"},
        )
        fig_bar.update_layout(
            margin=dict(t=20, b=20, l=10, r=10),
            height=300,
            coloraxis_showscale=False,
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")
    st.subheader("Submission Timeline")
    meta_copy = meta.copy()

    # parse dates – handle both YYYY-MM-DD and MM/DD/YYYY
    def parse_date_safe(s):
        for fmt in ("%Y-%m-%d", "%m/%d/%Y"):
            try:
                return pd.to_datetime(s, format=fmt)
            except Exception:
                pass
        return pd.NaT

    meta_copy["submitted_on_dt"] = meta_copy["submitted_on"].apply(parse_date_safe)
    timeline = meta_copy.dropna(subset=["submitted_on_dt"]) \
                        .groupby(meta_copy["submitted_on_dt"].dt.date) \
                        .size().reset_index(name="submissions")
    timeline.columns = ["date", "submissions"]
    fig_line = px.line(
        timeline, x="date", y="submissions",
        markers=True,
        labels={"date": "Date", "submissions": "Submissions"},
    )
    fig_line.update_traces(line_color="#2563eb", marker_color="#1e3a5f")
    fig_line.update_layout(margin=dict(t=10, b=10), height=250)
    st.plotly_chart(fig_line, use_container_width=True)


elif view == "== Department Status":
    st.markdown('<div class="section-header"> Panel 2 — Department Status</div>',
                unsafe_allow_html=True)

    # rename for display
    display_report = report.rename(columns={
        "department":                "Department",
        "datasets_submitted":        "Submitted",
        "approved":                  "Approved",
        "pending":                   "Pending",
        "approval_rate_pct":         "Approval Rate (%)",
        "followup_sent_all_pending": "Follow-up Sent",
        "no_response_after_7days":   "No Response 7d+",
    })

    # filters
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        dept_filter = st.multiselect(
            "Filter by Department",
            options=display_report["Department"].tolist(),
            default=[],
        )
    with col_f2:
        status_filter = st.selectbox(
            "Show departments with",
            ["All", "Pending items only", "Fully approved"],
        )

    filtered = display_report.copy()
    if dept_filter:
        filtered = filtered[filtered["Department"].isin(dept_filter)]
    if status_filter == "Pending items only":
        filtered = filtered[filtered["Pending"].astype(int) > 0]
    elif status_filter == "Fully approved":
        filtered = filtered[filtered["Pending"].astype(int) == 0]

    # colour the approval rate column
    def colour_approval(val):
        try:
            v = float(val)
        except Exception:
            return ""
        if v == 100:
            return "background-color: #dcfce7; color: #166534; font-weight:600"
        elif v >= 50:
            return "background-color: #fef9c3; color: #713f12"
        else:
            return "background-color: #fee2e2; color: #991b1b; font-weight:600"

    styled = filtered.style.applymap(colour_approval, subset=["Approval Rate (%)"])
    st.dataframe(styled, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("Approval Rate by Department")
    chart_data = report.copy()
    chart_data["approval_rate_pct"] = chart_data["approval_rate_pct"].astype(float)
    chart_data["approved"] = chart_data["approved"].astype(int)
    chart_data["pending"]  = chart_data["pending"].astype(int)

    fig_dept = px.bar(
        chart_data.sort_values("approval_rate_pct"),
        x="approval_rate_pct",
        y="department",
        orientation="h",
        color="approval_rate_pct",
        color_continuous_scale=["#ef4444", "#f97316", "#22c55e"],
        range_color=[0, 100],
        labels={"approval_rate_pct": "Approval Rate (%)", "department": ""},
        text="approval_rate_pct",
    )
    fig_dept.update_traces(texttemplate="%{text:.0f}%", textposition="outside")
    fig_dept.update_layout(
        height=600,
        margin=dict(l=10, r=40, t=10, b=10),
        coloraxis_showscale=False,
    )
    st.plotly_chart(fig_dept, use_container_width=True)


elif view == " Issue Breakdown":
    st.markdown('<div class="section-header"> Panel 3 — Issue Breakdown</div>',
                unsafe_allow_html=True)

    # expand issues into individual rows
    issue_rows = []
    for _, row in flags.iterrows():
        for issue in row["issues"].split(";"):
            issue = issue.strip()
            if issue:
                # bucket into broad categories
                if "owner" in issue.lower():
                    category = "Missing Data Owner"
                elif "description" in issue.lower():
                    category = "Missing / Short Description"
                elif "date format" in issue.lower() or "submitted_on" in issue.lower():
                    category = "Invalid Date Format"
                elif "dpdp" in issue.lower() or "personal data" in issue.lower():
                    category = "DPDP / Classification Mismatch"
                elif "classification" in issue.lower():
                    category = "Classification Missing"
                elif "record count" in issue.lower():
                    category = "Missing Record Count"
                else:
                    category = "Other"

                issue_rows.append({
                    "submission_id": row["submission_id"],
                    "department":    row["department"],
                    "raw_issue":     issue,
                    "category":      category,
                })

    issues_df = pd.DataFrame(issue_rows)

    # count by category
    cat_counts = issues_df.groupby("category").size().reset_index(name="count")
    cat_counts.sort_values("count", ascending=False, inplace=True)

    col1, col2 = st.columns([1.2, 1])
    with col1:
        st.subheader("Issue Frequency by Type")
        fig_issues = px.bar(
            cat_counts,
            x="count", y="category",
            orientation="h",
            color="count",
            color_continuous_scale="Reds",
            text="count",
            labels={"count": "# Occurrences", "category": "Issue Type"},
        )
        fig_issues.update_traces(textposition="outside")
        fig_issues.update_layout(
            height=380,
            margin=dict(l=10, r=30, t=10, b=10),
            coloraxis_showscale=False,
        )
        st.plotly_chart(fig_issues, use_container_width=True)

    with col2:
        st.subheader("Issue Share")
        fig_pie = px.pie(
            cat_counts, names="category", values="count",
            color_discrete_sequence=px.colors.qualitative.Set2,
            hole=0.4,
        )
        fig_pie.update_traces(textinfo="percent+label")
        fig_pie.update_layout(
            height=380,
            margin=dict(t=10, b=10, l=10, r=10),
            showlegend=False,
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("---")
    st.subheader("Issues by Department")
    dept_issue = issues_df.groupby(["department", "category"]).size().reset_index(name="count")
    fig_heat = px.bar(
        dept_issue,
        x="department", y="count",
        color="category",
        barmode="stack",
        color_discrete_sequence=px.colors.qualitative.Pastel,
        labels={"count": "Issues", "department": "Department", "category": "Issue Type"},
    )
    fig_heat.update_layout(
        height=420,
        margin=dict(l=10, r=10, t=10, b=120),
        xaxis_tickangle=-35,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    st.plotly_chart(fig_heat, use_container_width=True)

    st.markdown("---")
    st.subheader("All Flagged Submissions")
    st.dataframe(
        flags[["submission_id","department","dataset_title","issues"]],
        use_container_width=True,
        hide_index=True,
    )


elif view == "DPDP Flag Tracker":
    st.markdown('<div class="section-header">Panel 4 — DPDP Flag Tracker</div>',
                unsafe_allow_html=True)

    total_personal = len(dpdp)
    compliant      = len(dpdp[dpdp["fully_compliant"] == "Yes"])
    non_compliant  = total_personal - compliant

    c1, c2, c3 = st.columns(3)
    c1.metric("Datasets with Personal Data", total_personal)
    c2.metric("Fully DPDP-Compliant", compliant,
              delta=f"{compliant} OK", delta_color="normal")
    c3.metric("Non-Compliant", non_compliant,
              delta=f"{non_compliant} need action", delta_color="inverse")

    st.markdown("---")

    # traffic-light colouring
    def highlight_compliance(row):
        if row["fully_compliant"] != "Yes":
            return ["background-color: #fee2e2"] * len(row)
        return ["background-color: #dcfce7"] * len(row)

    def highlight_col(val):
        if val in ("No", "NO – action needed", "(blank)"):
            return "color: #991b1b; font-weight:700"
        if val == "Yes":
            return "color: #166534; font-weight:600"
        return ""

    display_dpdp = dpdp.rename(columns={
        "submission_id":          "ID",
        "department":             "Department",
        "dataset_title":          "Dataset",
        "data_classification":    "Classification",
        "classification_correct": "Class. Correct?",
        "data_steward_assigned":  "Steward Assigned?",
        "steward_ok":             "Steward OK?",
        "fully_compliant":        "Fully Compliant?",
    })

    styled_dpdp = display_dpdp.style \
        .apply(highlight_compliance, axis=1) \
        .applymap(highlight_col, subset=["Class. Correct?", "Steward OK?", "Fully Compliant?"])

    st.dataframe(styled_dpdp, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("Non-Compliant Personal Data Datasets – Action Required")
    nc = dpdp[dpdp["fully_compliant"] != "Yes"]
    if nc.empty:
        st.success("All personal data datasets are fully DPDP-compliant.")
    else:
        for _, row in nc.iterrows():
            reasons = []
            if row["classification_correct"] != "Yes":
                reasons.append(f"Classification is **{row['data_classification']}** — must be Restricted or Confidential")
            if row["steward_ok"] != "Yes":
                reasons.append("No Data Steward assigned")

            with st.expander(f" {row['submission_id']}  |  {row['department']}  –  {row['dataset_title']}"):
                for r in reasons:
                    st.markdown(f"- {r}")

    st.markdown("---")
    st.caption("A dataset is fully DPDP-compliant when: (1) classification is Restricted or Confidential, AND (2) a Data Steward has been assigned.")
