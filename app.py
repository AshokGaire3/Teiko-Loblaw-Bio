import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
import plotly.express as px
from scipy import stats
import os
import sys

DB_PATH  = "teiko_clinical.db"
CSV_PATH = "cell-count.csv"

# ── Auto-bootstrap DB on Streamlit Cloud ────────────────────────────────────
@st.cache_resource(show_spinner=False)
def ensure_database():
    if os.path.exists(DB_PATH):
        return
    if not os.path.exists(CSV_PATH):
        st.error(f"Source data file '{CSV_PATH}' not found.")
        st.stop()
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import load_data as ld
    with st.spinner("Initialising database from cell-count.csv…"):
        ld.init_db()
        ld.load_data()

ensure_database()

st.set_page_config(
    page_title="Loblaw Bio — Clinical Trial Dashboard",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

def get_conn():
    return sqlite3.connect(DB_PATH)

# ── Plotly theme ─────────────────────────────────────────────────────────────
BG   = "#0F1117"
SURF = "#161B27"
BDR  = "#232C3D"
BDR2 = "#2D3A50"
T1   = "#E2E8F0"   # primary text
T2   = "#8892A4"   # muted text
T3   = "#4A5568"   # dim text
ACC  = "#4F83CC"   # single accent — steel blue, used sparingly
RESP = "#6B93BE"   # responder — clear medium blue
NRSP = "#A07060"   # non-responder — muted terracotta (warm vs cool, clearly distinct)

def plot_theme(fig, h=310):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=SURF,
        plot_bgcolor=SURF,
        font=dict(family="Inter", color=T2, size=12),
        height=h,
        margin=dict(l=10, r=10, t=42, b=10),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=T1, size=11)),
    )
    fig.update_xaxes(
        gridcolor=BDR, linecolor=BDR2, zeroline=False,
        tickfont=dict(color=T2, size=11), title_font=dict(color=T1, size=12),
    )
    fig.update_yaxes(
        gridcolor=BDR, linecolor=BDR2, zeroline=False,
        tickfont=dict(color=T2, size=11), title_font=dict(color=T1, size=12),
    )

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif !important;
    background-color: {BG} !important;
    color: {T2} !important;
}}
h1, h2, h3, h4, h5, h6 {{
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    color: {T1} !important;
    letter-spacing: -0.015em !important;
}}

/* ── Hide Streamlit header / deploy button ── */
header[data-testid="stHeader"] {{
    height: 0 !important;
    min-height: 0 !important;
    overflow: hidden !important;
    padding: 0 !important;
}}
[data-testid="stToolbar"] {{ display: none !important; }}
#MainMenu {{ visibility: hidden !important; }}

/* Hide sidebar and its toggle completely */
[data-testid="stSidebar"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="stSidebarCollapseButton"],
button[kind="header"][data-testid="baseButton-header"] {{
    display: none !important;
    width: 0 !important;
    visibility: hidden !important;
}}

/* Full-width main content */
section[data-testid="stMainBlockContainer"] {{
    max-width: 100% !important;
    padding: 1rem 2.5rem !important;
}}

/* Scrollbar */
::-webkit-scrollbar {{ width: 4px; height: 4px; }}
::-webkit-scrollbar-track {{ background: {BG}; }}
::-webkit-scrollbar-thumb {{ background: {BDR2}; border-radius: 3px; }}

/* ── Tab bar ── */
div[data-testid="stTabBar"] {{
    background: transparent !important;
    border-bottom: 1px solid {BDR} !important;
    border-top: none !important;
    border-left: none !important;
    border-right: none !important;
    border-radius: 0 !important;
    padding: 0 !important;
    margin-bottom: 24px !important;
    gap: 0 !important;
    box-shadow: none !important;
}}
/* Kill the animated sliding indicator Streamlit renders */
div[data-testid="stTabBar"] > div[role="presentation"],
div[data-testid="stTabBar"] > div:not([role]),
div[data-testid="stTabBar"] > div:last-child {{
    display: none !important;
    height: 0 !important;
}}
/* All tabs base style */
button[data-baseweb="tab"] {{
    background: transparent !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    border-top: none !important;
    border-left: none !important;
    border-right: none !important;
    border-radius: 0 !important;
    outline: none !important;
    box-shadow: none !important;
    color: {T3} !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 10px 16px !important;
    margin: 0 !important;
    transition: color 0.15s !important;
    position: relative !important;
    bottom: -1px !important;
}}
button[data-baseweb="tab"]:hover {{
    color: {T1} !important;
    background: transparent !important;
    border-bottom: 2px solid {BDR2} !important;
}}
button[data-baseweb="tab"]:focus {{
    outline: none !important;
    box-shadow: none !important;
}}
button[data-baseweb="tab"][aria-selected="true"] {{
    color: {T1} !important;
    border-bottom: 2px solid {ACC} !important;
    background: transparent !important;
    font-weight: 600 !important;
}}

/* ── Cards ── */
.card {{
    background: {SURF};
    border: 1px solid {BDR};
    border-radius: 8px;
    padding: 18px 20px;
    margin-bottom: 14px;
}}
.stat-card {{
    background: {SURF};
    border: 1px solid {BDR};
    border-radius: 8px;
    padding: 18px 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    min-height: 100px;
}}
.stat-card:hover {{ border-color: {BDR2}; }}
.stat-label {{
    font-size: 10px;
    font-weight: 600;
    color: {T3};
    text-transform: uppercase;
    letter-spacing: 0.09em;
    margin-bottom: 6px;
}}
.stat-value {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 26px;
    font-weight: 500;
    color: {T1};
    line-height: 1;
}}
.stat-icon {{
    color: {T3};
    opacity: 0.7;
}}

/* ── Header bar ── */
.page-header {{
    border-bottom: 1px solid {BDR};
    padding-bottom: 18px;
    margin-bottom: 24px;
}}
.page-header h1 {{
    font-size: 22px !important;
    font-weight: 600 !important;
    color: {T1} !important;
    margin: 0 !important;
}}
.page-header p {{
    font-size: 13px !important;
    color: {T2} !important;
    margin: 4px 0 0 0 !important;
}}
.accent-tag {{
    display: inline-block;
    background: rgba(79,131,204,0.12);
    border: 1px solid rgba(79,131,204,0.25);
    color: {ACC};
    font-size: 11px;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 4px;
    vertical-align: middle;
    margin-left: 8px;
    letter-spacing: 0.04em;
}}

/* ── Section label ── */
.section-label {{
    font-size: 11px;
    font-weight: 600;
    color: {T3};
    text-transform: uppercase;
    letter-spacing: 0.09em;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid {BDR};
}}

/* ── Inputs ── */
div[data-baseweb="select"] > div {{
    background: {SURF} !important;
    border: 1px solid {BDR2} !important;
    border-radius: 6px !important;
    color: {T1} !important;
}}
div[data-baseweb="select"]:focus-within > div {{
    border-color: {ACC} !important;
    box-shadow: none !important;
}}
div[data-testid="stTextInput"] input {{
    background: {SURF} !important;
    border: 1px solid {BDR2} !important;
    border-radius: 6px !important;
    color: {T1} !important;
    padding: 8px 12px !important;
}}
div[data-testid="stTextInput"] input:focus {{
    border-color: {ACC} !important;
    box-shadow: none !important;
    outline: none !important;
}}
div[data-testid="stRadio"] label {{ color: {T2} !important; font-size: 13px !important; }}
div[data-testid="stRadio"] label:hover {{ color: {T1} !important; }}

/* ── Bordered container ── */
div[data-testid="stVerticalBlockBorderWrapper"] {{
    background: {SURF} !important;
    border: 1px solid {BDR} !important;
    border-radius: 8px !important;
    padding: 18px !important;
}}

/* ── Download button ── */
div.stDownloadButton > button {{
    background: transparent !important;
    color: {T1} !important;
    border: 1px solid {BDR2} !important;
    border-radius: 6px !important;
    padding: 7px 18px !important;
    font-weight: 500 !important;
    font-size: 13px !important;
    transition: border-color 0.15s !important;
}}
div.stDownloadButton > button:hover {{
    border-color: {ACC} !important;
    color: {ACC} !important;
    background: transparent !important;
}}

/* ── Dataframe ── */
div[data-testid="stDataFrame"] {{
    border: 1px solid {BDR} !important;
    border-radius: 8px !important;
    overflow: hidden !important;
}}

/* ── Alerts ── */
div[data-testid="stNotification"] {{
    background: {SURF} !important;
    border-radius: 6px !important;
}}

/* ── Body text ── */
div[data-testid="stMarkdownContainer"] p {{
    color: {T2} !important;
    font-size: 13px !important;
    line-height: 1.6 !important;
}}
hr {{ border-color: {BDR} !important; }}
</style>
""", unsafe_allow_html=True)

# ── Page header ──────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="page-header">
  <h1>🧬 Loblaw Bio — Clinical Trial Analytics <span class="accent-tag">LIVE</span></h1>
  <p>Immune cell population analysis · Drug candidate <strong style="color:{T1}">miraclib</strong></p>
</div>
""", unsafe_allow_html=True)

if not os.path.exists(DB_PATH):
    st.error("Database could not be initialised. Ensure cell-count.csv is in the repository root.")
    st.stop()

conn = get_conn()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="padding:12px 0 16px 0;">
      <div style="font-size:20px;margin-bottom:6px;">🧬</div>
      <div style="font-size:16px;font-weight:600;color:{T1};">Loblaw Bio</div>
      <div style="font-size:11px;color:{T3};text-transform:uppercase;letter-spacing:0.09em;margin-top:2px;">Clinical Trials Hub</div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()
    st.markdown(f'<div class="section-label">Drug Candidates</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="font-size:13px;color:{T2};line-height:2;">
      <div><span style="color:{T1};font-weight:500;">Miraclib</span> &nbsp;·&nbsp; Immunotherapy</div>
      <div>Phauximab &nbsp;·&nbsp; Monoclonal Ab</div>
      <div>Quintazide &nbsp;·&nbsp; Comparative</div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()
    st.info("Hover over charts to interact. Use filters in each tab to explore cohort subsets.")
    st.divider()
    st.markdown(f'<div style="font-size:11px;color:{T3};text-align:center;">Loblaw Bio Informatics</div>', unsafe_allow_html=True)

# ── DB stats ─────────────────────────────────────────────────────────────────
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM subjects;");  total_subjects = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM samples;");   total_samples  = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM projects;");  total_projects = cur.fetchone()[0]

# ── Tabs ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "Trial Overview",
    "Cell Frequencies",
    "Statistical Analysis",
    "Cohort Explorer",
])

# ═══════════════════════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════
with tab1:
    c1, c2, c3 = st.columns(3, gap="medium")
    def stat_card(col, label, value, icon_svg):
        col.markdown(f"""
        <div class="stat-card">
          <div>
            <div class="stat-label">{label}</div>
            <div class="stat-value">{value}</div>
          </div>
          <div class="stat-icon">{icon_svg}</div>
        </div>
        """, unsafe_allow_html=True)

    stat_card(c1, "Projects", str(total_projects),
        '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>')
    stat_card(c2, "Enrolled Subjects", f"{total_subjects:,}",
        '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>')
    stat_card(c3, "Biological Samples", f"{total_samples:,}",
        '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M10 2v7.31L3.75 20a1 1 0 0 0 .85 1.5h14.8a1 1 0 0 0 .85-1.5L14 9.3V2h-4z"/><path d="M8.5 2h7"/></svg>')

    st.markdown("<br>", unsafe_allow_html=True)

    df_meta = pd.read_sql_query("SELECT condition, treatment, response FROM subjects;", conn)

    col_l, col_r = st.columns([3, 2], gap="large")
    with col_l:
        st.markdown(f'<div class="section-label">Study Distribution</div>', unsafe_allow_html=True)
        cc1, cc2 = st.columns(2, gap="small")

        # Muted monochromatic palette for pie charts
        SLICE_COLORS = ["#4A5568", "#64748B", "#8892A4"]

        with cc1:
            fig = px.pie(df_meta, names="condition", hole=0.48,
                         color_discrete_sequence=SLICE_COLORS)
            plot_theme(fig, h=260)
            fig.update_layout(
                title=dict(text="Indication", font=dict(size=12, color=T1), x=0.5, xanchor="center"),
                legend=dict(orientation="h", y=-0.18, x=0.5, xanchor="center", font=dict(size=11, color=T2)),
                showlegend=True,
            )
            fig.update_traces(textinfo="percent", textfont=dict(color=T1, size=11),
                              marker=dict(line=dict(color=BG, width=2)))
            st.plotly_chart(fig, use_container_width=True)

        with cc2:
            df_r = df_meta["response"].value_counts().reset_index()
            df_r.columns = ["response", "count"]
            df_r["response"] = df_r["response"].fillna("Healthy")
            fig2 = px.pie(df_r, values="count", names="response", hole=0.48,
                          color_discrete_sequence=SLICE_COLORS)
            plot_theme(fig2, h=260)
            fig2.update_layout(
                title=dict(text="Response Status", font=dict(size=12, color=T1), x=0.5, xanchor="center"),
                legend=dict(orientation="h", y=-0.18, x=0.5, xanchor="center", font=dict(size=11, color=T2)),
            )
            fig2.update_traces(textinfo="percent", textfont=dict(color=T1, size=11),
                               marker=dict(line=dict(color=BG, width=2)))
            st.plotly_chart(fig2, use_container_width=True)

    with col_r:
        st.markdown(f'<div class="section-label">Treatment Arms</div>', unsafe_allow_html=True)
        df_tx = df_meta["treatment"].value_counts().reset_index()
        df_tx.columns = ["Treatment", "Patients"]
        st.dataframe(df_tx, use_container_width=True, hide_index=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f'<div class="section-label">Pipeline Note</div>', unsafe_allow_html=True)
        st.info(
            "**Quintazide** is being evaluated as a comparative agent for cohorts "
            "non-responsive to **miraclib** and **phauximab**. The 3NF schema "
            "supports ingesting new drug arms without schema changes."
        )

# ═══════════════════════════════════════════════════════════════════════════
# TAB 2 — CELL FREQUENCIES
# ═══════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown(f'<div class="section-label">Cell Population Relative Frequencies</div>', unsafe_allow_html=True)
    st.markdown("Relative frequency (%) of each immune cell type per sample — `count ÷ total_count × 100`")

    # Load data
    precomp = "output/initial_analysis_summary.csv"
    if os.path.exists(precomp):
        df_sum = pd.read_csv(precomp)
    else:
        q = """
        SELECT s.sample_id AS sample, c.b_cell, c.cd8_t_cell, c.cd4_t_cell, c.nk_cell, c.monocyte
        FROM samples s JOIN cell_counts c ON s.sample_id = c.sample_id;
        """
        df_all = pd.read_sql_query(q, conn)
        pops = ["b_cell", "cd8_t_cell", "cd4_t_cell", "nk_cell", "monocyte"]
        df_all["total_count"] = df_all[pops].sum(axis=1)
        rows = []
        for _, r in df_all.iterrows():
            tot = r["total_count"]
            for p in pops:
                rows.append({"sample": r["sample"], "total_count": int(tot), "population": p,
                             "count": int(r[p]), "percentage": round((r[p]/tot*100) if tot else 0, 4)})
        df_sum = pd.DataFrame(rows)

    # Filters — inline, not in a box
    col_a, col_b, col_spacer = st.columns([2, 2, 4], gap="medium")
    with col_a:
        search_sample = st.text_input("Sample ID", placeholder="e.g. sample00000", key="t2_s")
    with col_b:
        search_pop = st.selectbox("Population", ["All","b_cell","cd8_t_cell","cd4_t_cell","nk_cell","monocyte"], key="t2_p")

    df_f = df_sum.copy()
    if search_sample:
        df_f = df_f[df_f["sample"].str.contains(search_sample, case=False)]
    if search_pop != "All":
        df_f = df_f[df_f["population"] == search_pop]

    st.markdown(f'<div style="font-size:12px;color:{T3};margin-bottom:8px;">Showing {min(len(df_f),1000):,} of {len(df_f):,} rows</div>', unsafe_allow_html=True)
    st.dataframe(df_f.head(1000), use_container_width=True, hide_index=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_dl, _ = st.columns([2, 6])
    with col_dl:
        st.download_button(
            label="Download CSV",
            data=df_sum.to_csv(index=False).encode("utf-8"),
            file_name="cell_frequencies_summary.csv",
            mime="text/csv",
            use_container_width=True,
        )

# ═══════════════════════════════════════════════════════════════════════════
# TAB 3 — STATISTICAL ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown(f'<div class="section-label">Responders vs Non-Responders · Melanoma · Miraclib · PBMC</div>', unsafe_allow_html=True)

    col_tf, _ = st.columns([3, 5])
    with col_tf:
        time_filter = st.radio("Timepoint", ["All timepoints", "Baseline only (t = 0)"],
                               horizontal=True, key="t3_tf")
    time_val = 0 if "Baseline" in time_filter else None

    q_stat = """
    SELECT s.sample_id, sub.response, s.time_from_treatment_start,
           c.b_cell, c.cd8_t_cell, c.cd4_t_cell, c.nk_cell, c.monocyte
    FROM samples s
    JOIN subjects sub ON s.subject_id = sub.subject_id
    JOIN cell_counts c ON s.sample_id = c.sample_id
    WHERE sub.condition = 'melanoma' AND sub.treatment = 'miraclib'
      AND s.sample_type = 'PBMC' AND sub.response IN ('yes', 'no')
    """
    if time_val is not None:
        q_stat += f" AND s.time_from_treatment_start = {time_val}"

    df_st = pd.read_sql_query(q_stat, conn)
    pops  = ["b_cell", "cd8_t_cell", "cd4_t_cell", "nk_cell", "monocyte"]
    df_st["total_count"] = df_st[pops].sum(axis=1)
    for p in pops:
        df_st[p + "_pct"] = df_st[p] / df_st["total_count"] * 100

    n_r  = (df_st["response"] == "yes").sum()
    n_nr = (df_st["response"] == "no").sum()

    # Cohort summary — plain text, no badges
    st.markdown(f"""
    <div style="font-size:13px;color:{T2};margin:10px 0 20px 0;">
      <span style="color:{T1};font-weight:500;">{len(df_st)}</span> samples &nbsp;·&nbsp;
      <span style="color:{T1};font-weight:500;">{n_r}</span> responders &nbsp;·&nbsp;
      <span style="color:{T1};font-weight:500;">{n_nr}</span> non-responders
    </div>
    """, unsafe_allow_html=True)

    stat_rows = []
    row1 = st.columns(3, gap="small")
    # For last 2 charts, centre them
    _, col_4, col_5, _ = st.columns([0.5, 1, 1, 0.5], gap="small")
    row2 = [col_4, col_5]

    for i, pop in enumerate(pops):
        pct = pop + "_pct"
        r_v  = df_st[df_st["response"] == "yes"][pct]
        nr_v = df_st[df_st["response"] == "no"][pct]

        _, t_pval  = stats.ttest_ind(r_v, nr_v, equal_var=False)
        _, u_pval  = stats.mannwhitneyu(r_v, nr_v, alternative="two-sided")

        stat_rows.append({
            "Cell Type":           pop.replace("_", " ").title(),
            "Responder Mean":      f"{r_v.mean():.3f}%",
            "Non-Responder Mean":  f"{nr_v.mean():.3f}%",
            "t-test p":            f"{t_pval:.6f}",
            "Mann-Whitney p":      f"{u_pval:.6f}",
            "Significant (α=0.05)": "Yes" if t_pval < 0.05 else "No",
        })

        title_text = pop.replace("_", " ").title()
        p_annot    = f"p = {t_pval:.4f}" + (" *" if t_pval < 0.05 else "")

        fig = px.box(
            df_st, x="response", y=pct, color="response",
            color_discrete_map={"yes": RESP, "no": NRSP},
            labels={"response": "", pct: "Frequency (%)"},
            points="outliers",
        )
        plot_theme(fig, h=290)
        fig.update_layout(
            showlegend=False,
            title=dict(
                text=f"{title_text}   <span style='font-size:11px;color:{T3};'>{p_annot}</span>",
                font=dict(size=13, color=T1), x=0.5, xanchor="center",
            ),
            xaxis=dict(
                categoryorder="array", categoryarray=["no", "yes"],
                ticktext=["Non-resp.", "Responder"], tickvals=["no", "yes"],
            ),
        )
        fig.update_traces(line_width=1.2, marker=dict(size=3, opacity=0.5), boxmean=True)

        if i < 3:
            row1[i].plotly_chart(fig, use_container_width=True)
        else:
            row2[i - 3].plotly_chart(fig, use_container_width=True)

    st.markdown(f'<div class="section-label" style="margin-top:8px;">Statistical Results</div>', unsafe_allow_html=True)
    st.dataframe(pd.DataFrame(stat_rows), use_container_width=True, hide_index=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if time_val is None:
        st.success(
            "**CD4+ T-cell frequency** is the only population with a statistically significant "
            "difference between responders and non-responders (Welch's t-test *p* = 0.0050, "
            "Mann-Whitney *p* = 0.0133). Responders show a higher proportion of CD4+ T-cells "
            "(30.54% vs 29.90%). No other populations reach significance."
        )
    else:
        st.warning(
            "At baseline (t = 0), no immune cell populations show a statistically significant "
            "difference between responders and non-responders (all *p* > 0.20). "
            "The CD4+ T-cell signal emerges during treatment, not before it."
        )

# ═══════════════════════════════════════════════════════════════════════════
# TAB 4 — COHORT EXPLORER
# ═══════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown(f'<div class="section-label">Query Builder · Baseline Melanoma Filter Active</div>', unsafe_allow_html=True)

    with st.container(border=True):
        cf1, cf2, cf3, cf4 = st.columns(4, gap="medium")
        with cf1: sel_cond = st.selectbox("Indication",   ["melanoma", "carcinoma", "healthy"], key="t4_c")
        with cf2: sel_type = st.selectbox("Sample Type",  ["PBMC", "WB"],                       key="t4_t")
        with cf3: sel_time = st.selectbox("Day",          [0, 7, 14],                            key="t4_d")
        with cf4: sel_tx   = st.selectbox("Treatment",    ["miraclib", "phauximab", "none"],     key="t4_x")

    q_cohort = f"""
    SELECT s.sample_id, sub.subject_id, sub.project_id, sub.response, sub.sex, c.b_cell
    FROM samples s
    JOIN subjects sub ON s.subject_id = sub.subject_id
    JOIN cell_counts c ON s.sample_id = c.sample_id
    WHERE sub.condition = '{sel_cond}' AND s.sample_type = '{sel_type}'
      AND s.time_from_treatment_start = {sel_time} AND sub.treatment = '{sel_tx}';
    """
    df_c = pd.read_sql_query(q_cohort, conn)

    st.markdown(f"""
    <div style="font-size:13px;color:{T2};margin:10px 0 20px 0;">
      Cohort size: <span style="color:{T1};font-weight:600;font-size:20px;">{len(df_c):,}</span> samples
    </div>
    """, unsafe_allow_html=True)

    if len(df_c) == 0:
        st.warning("No samples match these filters.")
    else:
        def simple_bar(df_val, x_col, y_col):
            fig = px.bar(df_val, x=x_col, y=y_col, text=y_col,
                         color_discrete_sequence=[ACC])
            plot_theme(fig, h=270)
            fig.update_layout(showlegend=False)
            fig.update_traces(textposition="outside", cliponaxis=False,
                              marker_line_width=0, textfont=dict(color=T1, size=12),
                              marker_color=BDR2)
            return fig

        cr1, cr2, cr3 = st.columns(3, gap="medium")

        with cr1:
            st.markdown(f'<div style="font-size:12px;color:{T2};margin-bottom:6px;font-weight:500;">Samples per Project</div>', unsafe_allow_html=True)
            df_p = df_c["project_id"].value_counts().reset_index()
            df_p.columns = ["Project", "Samples"]
            fig_p = px.bar(df_p, x="Project", y="Samples", text="Samples",
                           color_discrete_sequence=[BDR2])
            plot_theme(fig_p, h=270)
            fig_p.update_layout(showlegend=False)
            fig_p.update_traces(textposition="outside", cliponaxis=False,
                                marker_line_width=0, textfont=dict(color=T1, size=12))
            st.plotly_chart(fig_p, use_container_width=True)

        with cr2:
            st.markdown(f'<div style="font-size:12px;color:{T2};margin-bottom:6px;font-weight:500;">Response Status</div>', unsafe_allow_html=True)
            df_r = df_c["response"].value_counts().reset_index()
            df_r.columns = ["Response", "Count"]
            df_r["Response"] = df_r["Response"].fillna("Healthy")
            fig_r = px.bar(df_r, x="Response", y="Count", text="Count",
                           color_discrete_sequence=[BDR2])
            plot_theme(fig_r, h=270)
            fig_r.update_layout(showlegend=False)
            fig_r.update_traces(textposition="outside", cliponaxis=False,
                                marker_line_width=0, textfont=dict(color=T1, size=12))
            st.plotly_chart(fig_r, use_container_width=True)

        with cr3:
            st.markdown(f'<div style="font-size:12px;color:{T2};margin-bottom:6px;font-weight:500;">Sex Distribution</div>', unsafe_allow_html=True)
            df_s = df_c["sex"].value_counts().reset_index()
            df_s.columns = ["Sex", "Count"]
            fig_s = px.bar(df_s, x="Sex", y="Count", text="Count",
                           color_discrete_sequence=[BDR2])
            plot_theme(fig_s, h=270)
            fig_s.update_layout(showlegend=False)
            fig_s.update_traces(textposition="outside", cliponaxis=False,
                                marker_line_width=0, textfont=dict(color=T1, size=12))
            st.plotly_chart(fig_s, use_container_width=True)

        st.divider()

        # B-cell averages
        males_resp   = df_c[(df_c["sex"] == "M") & (df_c["response"] == "yes")]
        avg_a        = males_resp["b_cell"].mean() if len(males_resp) > 0 else 0.0

        q_any = f"""
        SELECT c.b_cell FROM samples s
        JOIN subjects sub ON s.subject_id = sub.subject_id
        JOIN cell_counts c ON s.sample_id = c.sample_id
        WHERE sub.condition = '{sel_cond}' AND s.sample_type = '{sel_type}'
          AND s.time_from_treatment_start = {sel_time}
          AND sub.sex = 'M' AND sub.response = 'yes';
        """
        df_any = pd.read_sql_query(q_any, conn)
        avg_b  = df_any["b_cell"].mean() if len(df_any) > 0 else 0.0

        st.markdown(f'<div style="font-size:12px;color:{T2};font-weight:500;margin-bottom:12px;">Avg B-cells — Male Responders at day {sel_time}</div>', unsafe_allow_html=True)

        mc1, mc2, _ = st.columns([2, 2, 4], gap="medium")
        with mc1:
            st.markdown(f"""
            <div class="stat-card">
              <div>
                <div class="stat-label">Case A · {sel_tx} only</div>
                <div class="stat-value">{avg_a:,.2f}</div>
                <div style="font-size:11px;color:{T3};margin-top:5px;">{len(males_resp)} subjects</div>
              </div>
            </div>
            """, unsafe_allow_html=True)
        with mc2:
            st.markdown(f"""
            <div class="stat-card">
              <div>
                <div class="stat-label">Case B · all treatments</div>
                <div class="stat-value">{avg_b:,.2f}</div>
                <div style="font-size:11px;color:{T3};margin-top:5px;">{len(df_any)} subjects</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

conn.close()
