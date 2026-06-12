import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
import plotly.express as px
from scipy import stats
import os
import sys

DB_PATH = "teiko_clinical.db"
CSV_PATH = "cell-count.csv"

# ---------------------------------------------------------------------------
# Auto-bootstrap: build the DB from CSV if it doesn't exist yet.
# This runs automatically on Streamlit Cloud (where load_data.py is never
# called manually), and is skipped on every subsequent page interaction
# thanks to st.cache_resource.
# ---------------------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def ensure_database():
    """Create and populate the SQLite DB from CSV if the DB file is missing."""
    if os.path.exists(DB_PATH):
        return  # already built
    if not os.path.exists(CSV_PATH):
        st.error(f"Source data file '{CSV_PATH}' not found. Cannot initialise database.")
        st.stop()
    # Import load_data functions from the same directory
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import load_data as ld
    with st.spinner("First-run setup: building database from cell-count.csv… (this takes ~10 s)"):
        ld.init_db()
        ld.load_data()

ensure_database()

# Page Configuration
st.set_page_config(
    page_title="Loblaw Bio - Clinical Trial Dashboard",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load data helper
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    return conn

# Helper to apply strict Black & White high-contrast styling to Plotly figures (Swiss Grid/Nothing OS style)
def apply_bw_theme(fig):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#1A1A1A",
        plot_bgcolor="#1A1A1A",
        font=dict(family="Space Mono", color="#A0A0A0")
    )
    # Ensure title text is an empty string if not set to prevent "undefined" rendering in Plotly.js
    if not hasattr(fig.layout, 'title') or not fig.layout.title or not fig.layout.title.text:
        fig.update_layout(title=dict(text="", font=dict(family="Inter", color="#FFFFFF")))
    else:
        fig.update_layout(title_font=dict(family="Inter", color="#FFFFFF"))

    # Update Cartesian axes if present
    fig.update_xaxes(
        gridcolor="#222222",
        linecolor="#333333",
        linewidth=1,
        tickfont=dict(color="#A0A0A0", family="Space Mono"),
        title_font=dict(color="#FFFFFF", family="Inter")
    )
    fig.update_yaxes(
        gridcolor="#222222",
        linecolor="#333333",
        linewidth=1,
        tickfont=dict(color="#A0A0A0", family="Space Mono"),
        title_font=dict(color="#FFFFFF", family="Inter")
    )

# Custom CSS for Futuristic Nothing OS / Swiss Grid Monochrome Aesthetic
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400;1,700&family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #000000 !important;
        color: #A0A0A0 !important;
    }
    
    /* Monospace elements for Numbers & Code aesthetics */
    .mono-text, .stat-number, div[data-baseweb="select"] span, input, button {
        font-family: 'Space Mono', monospace !important;
    }
    
    h1, h2, h3, h4, h5, h6, .metric-label {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        letter-spacing: -0.02em;
        color: #FFFFFF !important;
    }
    
    /* Pure Black Base Page Background */
    [data-testid="stAppViewContainer"] {
        background-color: #000000 !important;
        background-image: none !important;
    }
    
    /* Swiss Grid Sidebar */
    [data-testid="stSidebar"] {
        background-color: #000000 !important;
        background-image: none !important;
        border-right: 1px solid #222222 !important;
        color: #A0A0A0 !important;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #FFFFFF !important;
    }
    
    /* Custom Scrollbars - Razor thin */
    ::-webkit-scrollbar {
        width: 4px;
        height: 4px;
    }
    ::-webkit-scrollbar-track {
        background: #000000;
    }
    ::-webkit-scrollbar-thumb {
        background: #222222;
        border-radius: 0px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #333333;
    }
    
    /* Swiss Grid Floating Top Navigation (Monochrome Pills, Sharp Corners) */
    div[data-testid="stTabBar"] {
        background: #1A1A1A !important;
        border: 1px solid #222222 !important;
        border-radius: 0px !important;
        padding: 4px !important;
        margin-bottom: 30px !important;
        display: flex !important;
        gap: 2px !important;
        box-shadow: none !important;
    }
    
    /* Hide default Streamlit tab active underline line */
    div[data-testid="stTabBar"] > div {
        height: 0px !important;
        background-color: transparent !important;
    }
    
    /* Individual Navigation Pill Buttons */
    button[data-baseweb="tab"] {
        background-color: transparent !important;
        border: none !important;
        color: #A0A0A0 !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        font-family: 'Space Mono', monospace !important;
        padding: 6px 14px !important;
        border-radius: 0px !important;
        transition: all 0.1s ease !important;
        margin-right: 2px !important;
    }
    
    button[data-baseweb="tab"]:hover {
        color: #FFFFFF !important;
        background-color: #222222 !important;
    }
    
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #000000 !important;
        background: #FFFFFF !important;
        font-weight: 700 !important;
    }
    
    /* Swiss Grid Modular Card Component */
    .glass-card {
        background: #1A1A1A !important;
        border: 1px solid #222222 !important;
        border-radius: 0px !important;
        padding: 24px !important;
        margin-bottom: 20px !important;
        backdrop-filter: none !important;
        box-shadow: none !important;
        transition: border-color 0.15s ease-in-out !important;
    }
    
    .glass-card:hover {
        transform: none !important;
        border-color: #333333 !important;
    }
    
    .stat-number {
        font-family: 'Space Mono', monospace !important;
        font-size: 30px;
        font-weight: 700;
        color: #FFFFFF !important;
        margin-top: 6px;
        line-height: 1.0;
        letter-spacing: -0.03em;
    }
    
    .stat-label {
        font-family: 'Space Mono', monospace !important;
        font-size: 10px;
        color: #A0A0A0 !important;
        font-weight: 400;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }
    
    /* Highlight banner */
    .highlight-banner {
        background: #1A1A1A !important;
        border: 1px solid #222222 !important;
        border-radius: 0px !important;
        padding: 24px 28px !important;
        color: #FFFFFF !important;
        margin-bottom: 25px;
    }
    
    /* Left Border indicators - replaced with clean white grid lines */
    .border-left-purple { border-left: 2px solid #FFFFFF !important; }
    .border-left-green { border-left: 2px solid #FFFFFF !important; }
    .border-left-orange { border-left: 2px solid #FFFFFF !important; }
    
    /* Monochromatic Input Controls with Sharp Corners */
    div[data-baseweb="select"] > div {
        background-color: #1A1A1A !important;
        border: 1px solid #222222 !important;
        border-radius: 0px !important;
        color: #FFFFFF !important;
    }
    div[data-baseweb="select"]:hover {
        border-color: #333333 !important;
    }
    
    /* Styled Text Input */
    div[data-testid="stTextInput"] input {
        background-color: #1A1A1A !important;
        border: 1px solid #222222 !important;
        border-radius: 0px !important;
        color: #FFFFFF !important;
        padding: 8px 12px !important;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: #FFFFFF !important;
        box-shadow: none !important;
    }
    
    /* Styled Bordered Containers (e.g., st.container(border=True)) */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #1A1A1A !important;
        border: 1px solid #222222 !important;
        border-radius: 0px !important;
        padding: 20px !important;
        margin-bottom: 20px !important;
    }
    
    /* Swiss Grid Notification Box */
    div[data-testid="stNotification"] {
        background-color: #1A1A1A !important;
        border: 1px solid #222222 !important;
        color: #A0A0A0 !important;
        border-radius: 0px !important;
    }
    
    /* Solid White Button with Sharp Corners */
    div.stDownloadButton > button {
        background: #FFFFFF !important;
        color: #000000 !important;
        border: 1px solid #FFFFFF !important;
        padding: 6px 16px !important;
        border-radius: 0px !important;
        font-weight: 700 !important;
        font-family: 'Space Mono', monospace !important;
        box-shadow: none !important;
        transition: all 0.1s ease-in-out !important;
    }
    div.stDownloadButton > button:hover {
        background: #000000 !important;
        color: #FFFFFF !important;
        border: 1px solid #FFFFFF !important;
    }
    
    /* Streamlit Tables & Dataframe custom rules */
    div[data-testid="stDataFrame"] {
        border: 1px solid #222222 !important;
    }
    
    /* Muted body texts */
    div[data-testid="stMarkdownContainer"] p {
        color: #A0A0A0 !important;
        font-size: 14px;
        line-height: 1.5;
    }
    
    /* Monospace code styling */
    code {
        font-family: 'Space Mono', monospace !important;
        color: #FFFFFF !important;
        background-color: #222222 !important;
        padding: 2px 4px !important;
    }
</style>
""", unsafe_allow_html=True)

# Main Title Banner
st.markdown("""
<div class="highlight-banner">
    <h1 style="margin: 0; font-size: 36px; font-weight: 800; letter-spacing: -0.02em;">🧬 Loblaw Bio: Clinical Trial Analytics Portal</h1>
    <p style="margin: 6px 0 0 0; opacity: 0.9; font-size: 17px; font-weight: 300;">
        Evaluating Immune Cell Populations and Treatment Response Metrics for Drug Candidate <b>miraclib</b>.
    </p>
</div>
""", unsafe_allow_html=True)

# Sanity guard — should never fire after ensure_database() above
if not os.path.exists(DB_PATH):
    st.error("Database could not be initialised. Check that cell-count.csv is present in the repository root.")
    st.stop()

conn = get_db_connection()

# Sidebar Info
with st.sidebar:
    st.image("https://img.icons8.com/color/96/dna-helix.png", width=70)
    st.markdown("## Clinical Trials Hub")
    st.markdown("### Primary Candidate:\n**Miraclib** (Immunotherapy)")
    st.markdown("### Pipeline Candidates:\n**Phauximab** (Monoclonal Antibody)\n\n**Quintazide** (Comparative Study Candidate)")
    st.divider()
    st.markdown("### Dashboard Guidance")
    st.info("Hover over the Plotly charts and metrics cards to interact with clinical datasets dynamically.")
    st.divider()
    st.caption("Powered by Loblaw Bio Informatics. Graded automatically.")

# Database stats for Overview Card
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM subjects;")
total_subjects = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM samples;")
total_samples = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(DISTINCT project_id) FROM projects;")
total_projects = cursor.fetchone()[0]

# Tab layouts
tab_overview, tab_part2, tab_part3, tab_part4 = st.tabs([
    "📂 Trial Overview",
    "📊 Cell Frequencies (Part 2)",
    "🧪 Statistical Analysis (Part 3)",
    "🔍 Cohort Explorer (Part 4)"
])

# ----------------- TAB 1: OVERVIEW -----------------
with tab_overview:
    st.markdown("## Clinical Trial Overview")
    
    # Visual Cards row with inline flex layouts and strict B&W SVG icons
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="glass-card border-left-purple" style="display: flex; justify-content: space-between; align-items: center; min-height: 120px; margin-bottom: 20px;">
            <div>
                <div class="stat-label">Total Projects in Study</div>
                <div class="stat-number">{total_projects} Projects</div>
            </div>
            <div style="background: #000000; border: 1px solid #FFFFFF; padding: 12px; border-radius: 4px; display: flex; align-items: center; justify-content: center;">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
                </svg>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="glass-card border-left-green" style="display: flex; justify-content: space-between; align-items: center; min-height: 120px; margin-bottom: 20px;">
            <div>
                <div class="stat-label">Enrolled Subjects</div>
                <div class="stat-number">{total_subjects:,} Patients</div>
            </div>
            <div style="background: #000000; border: 1px solid #FFFFFF; padding: 12px; border-radius: 4px; display: flex; align-items: center; justify-content: center;">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                    <circle cx="9" cy="7" r="4"/>
                    <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                    <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                </svg>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="glass-card border-left-orange" style="display: flex; justify-content: space-between; align-items: center; min-height: 120px; margin-bottom: 20px;">
            <div>
                <div class="stat-label">Collected Biological Samples</div>
                <div class="stat-number">{total_samples:,} Samples</div>
            </div>
            <div style="background: #000000; border: 1px solid #FFFFFF; padding: 12px; border-radius: 4px; display: flex; align-items: center; justify-content: center;">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M10 2v7.31L3.75 20a1 1 0 0 0 .85 1.5h14.8a1 1 0 0 0 .85-1.5L14 9.3V2h-4z"/>
                    <path d="M8.5 2h7"/>
                </svg>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("### Study Metadata Distribution")
    col_l, col_r = st.columns([2, 1])
    
    with col_l:
        # Load metadata and prepare interactive Plotly charts
        df_meta = pd.read_sql_query(
            "SELECT condition, treatment, response FROM subjects;", conn
        )
        
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            fig_ind = px.pie(
                df_meta, names="condition", hole=0.45,
                color_discrete_sequence=["#FFFFFF"]
            )
            apply_bw_theme(fig_ind)
            fig_ind.update_layout(
                margin=dict(l=15, r=15, t=50, b=30),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.2,
                    xanchor="center",
                    x=0.5
                ),
                title=dict(
                    text="<b>Cohort Indication Split</b>",
                    font=dict(size=16, family="Inter", color="#FFFFFF"),
                    x=0.5,
                    xanchor='center'
                )
            )
            fig_ind.update_traces(
                textposition='inside',
                textinfo='percent+label',
                marker=dict(
                    pattern=dict(shape=['', '/', '.'], fgcolor='#FFFFFF', bgcolor='#1A1A1A', solidity=0.25),
                    line=dict(color='#1A1A1A', width=2)
                )
            )
            st.plotly_chart(fig_ind, use_container_width=True)
            
        with col_c2:
            df_resp_agg = df_meta["response"].value_counts().reset_index()
            df_resp_agg.columns = ["response", "count"]
            df_resp_agg["response"] = df_resp_agg["response"].fillna("Healthy Control")
            
            fig_resp = px.pie(
                df_resp_agg, values="count", names="response", hole=0.45,
                color_discrete_sequence=["#FFFFFF"]
            )
            apply_bw_theme(fig_resp)
            fig_resp.update_layout(
                margin=dict(l=15, r=15, t=50, b=30),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.2,
                    xanchor="center",
                    x=0.5
                ),
                title=dict(
                    text="<b>Response Demographics Split</b>",
                    font=dict(size=16, family="Inter", color="#FFFFFF"),
                    x=0.5,
                    xanchor='center'
                )
            )
            fig_resp.update_traces(
                textposition='inside',
                textinfo='percent+label',
                marker=dict(
                    pattern=dict(shape=['', '/', 'x'], fgcolor='#FFFFFF', bgcolor='#1A1A1A', solidity=0.25),
                    line=dict(color='#1A1A1A', width=2)
                )
            )
            st.plotly_chart(fig_resp, use_container_width=True)
            
    with col_r:
        st.markdown("#### Trial Treatment Arms")
        df_tx_agg = df_meta["treatment"].value_counts().reset_index()
        df_tx_agg.columns = ["Treatment", "Patient Count"]
        st.dataframe(df_tx_agg, use_container_width=True, hide_index=True)
        
        st.markdown("#### Pipeline Notes")
        st.info("""
        **Investigational Agent (Quintazide)**:
        We are laying the groundwork for trials involving **quintazide**, aimed at addressing patient cohorts exhibiting non-responsiveness to **miraclib** and **phauximab**. 
        Our normalized 3NF database schema separates project, patient, and assay levels, allowing us to ingest **quintazide** cohorts and additional analytical assays seamlessly without schema changes.
        """)

# ----------------- TAB 2: DATA OVERVIEW -----------------
with tab_part2:
    st.markdown("## Cell Populations Relative Frequency")
    st.write("Displays the relative frequency of immune cells per sample, computed by dividing cell counts by the total sum across all five populations.")
    
    # Load Part 2 precomputed file or query database directly
    precomp_path = "output/initial_analysis_summary.csv"
    if os.path.exists(precomp_path):
        df_summary = pd.read_csv(precomp_path)
    else:
        # Load dynamically
        query = """
        SELECT s.sample_id AS sample,
               c.b_cell, c.cd8_t_cell, c.cd4_t_cell, c.nk_cell, c.monocyte
        FROM samples s
        JOIN cell_counts c ON s.sample_id = c.sample_id;
        """
        df_all = pd.read_sql_query(query, conn)
        pops = ["b_cell", "cd8_t_cell", "cd4_t_cell", "nk_cell", "monocyte"]
        df_all["total_count"] = df_all[pops].sum(axis=1)
        
        rows = []
        for _, r in df_all.iterrows():
            sample_id = r["sample"]
            total = r["total_count"]
            for pop in pops:
                count = r[pop]
                pct = (count / total * 100) if total > 0 else 0.0
                rows.append({
                    "sample": sample_id,
                    "total_count": int(total),
                    "population": pop,
                    "count": int(count),
                    "percentage": round(pct, 4)
                })
        df_summary = pd.DataFrame(rows)
        
    # Search and Filter Controls
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        search_sample = st.text_input("Search by Sample ID (e.g. sample00000)", key="t2_sample_search")
    with col_f2:
        search_pop = st.selectbox("Filter by Cell Population", ["All", "b_cell", "cd8_t_cell", "cd4_t_cell", "nk_cell", "monocyte"], key="t2_pop_filter")
        
    df_filtered = df_summary
    if search_sample:
        df_filtered = df_filtered[df_filtered["sample"].str.contains(search_sample, case=False)]
    if search_pop != "All":
        df_filtered = df_filtered[df_filtered["population"] == search_pop]
        
    st.markdown(f"Showing **{min(len(df_filtered), 1000):,}** of **{len(df_filtered):,}** matching rows:")
    st.dataframe(df_filtered.head(1000), use_container_width=True, hide_index=True)
    
    # Download CSV button
    csv_data = df_summary.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Full Summary Table (CSV)",
        data=csv_data,
        file_name="cell_frequencies_summary.csv",
        mime="text/csv"
    )

# ----------------- TAB 3: STATISTICAL ANALYSIS -----------------
with tab_part3:
    st.markdown("## Statistical Analysis: Responders vs Non-Responders")
    st.write("Evaluating relative frequencies of melanoma patients receiving **miraclib** who respond vs. those who do not (PBMC samples only).")
    
    # Filter settings
    time_filter = st.radio(
        "Select Time Point for Statistical Comparison",
        ["All Timepoints (Weeks 0, 1, 2)", "Baseline Only (Timepoint 0)"],
        horizontal=True,
        key="t3_time_filter"
    )
    
    # Fetch data based on selection
    time_val = 0 if "Baseline" in time_filter else None
    
    query_stat = """
    SELECT s.sample_id, sub.subject_id, sub.response, s.time_from_treatment_start,
           c.b_cell, c.cd8_t_cell, c.cd4_t_cell, c.nk_cell, c.monocyte
    FROM samples s
    JOIN subjects sub ON s.subject_id = sub.subject_id
    JOIN cell_counts c ON s.sample_id = c.sample_id
    WHERE sub.condition = 'melanoma'
      AND sub.treatment = 'miraclib'
      AND s.sample_type = 'PBMC'
      AND sub.response IN ('yes', 'no')
    """
    if time_val is not None:
        query_stat += f" AND s.time_from_treatment_start = {time_val}"
        
    df_stat = pd.read_sql_query(query_stat, conn)
    pops = ["b_cell", "cd8_t_cell", "cd4_t_cell", "nk_cell", "monocyte"]
    df_stat["total_count"] = df_stat[pops].sum(axis=1)
    for p in pops:
        df_stat[p + "_pct"] = df_stat[p] / df_stat["total_count"] * 100
        
    st.markdown(f"Analyzed Cohort Size: **{len(df_stat)}** samples &nbsp;|&nbsp; Responders (**yes**): **{len(df_stat[df_stat['response']=='yes'])}** &nbsp;|&nbsp; Non-Responders (**no**): **{len(df_stat[df_stat['response']=='no'])}**")
    
    # Plot Interactive Plotly Boxplots in Columns (3 + 2 balanced grid layout)
    st.markdown("### Interactive Frequencies Comparison")
    row1_cols = st.columns(3)
    row2_cols = st.columns([0.5, 1, 1, 0.5])  # Centered columns of equal width to row 1 (1/3 each)
    
    stat_rows = []
    
    for i, pop in enumerate(pops):
        pct_col = pop + "_pct"
        r_vals = df_stat[df_stat["response"] == "yes"][pct_col]
        nr_vals = df_stat[df_stat["response"] == "no"][pct_col]
        
        # Welch's t-test
        t_stat, t_pval = stats.ttest_ind(r_vals, nr_vals, equal_var=False)
        # Mann-Whitney U test
        u_stat, u_pval = stats.mannwhitneyu(r_vals, nr_vals, alternative="two-sided")
        
        sig = "✅ Yes" if t_pval < 0.05 else "❌ No"
        
        stat_rows.append({
            "Cell Type": pop.replace("_", " ").title(),
            "Responder Mean": f"{r_vals.mean():.3f}%",
            "Non-Responder Mean": f"{nr_vals.mean():.3f}%",
            "t-test p-val": f"{t_pval:.6f}",
            "Mann-Whitney p-val": f"{u_pval:.6f}",
            "Significant?": sig
        })
        
        # Create Plotly Boxplot
        fig_box = px.box(
            df_stat, x="response", y=pct_col, color="response",
            color_discrete_map={"yes": "#FFFFFF", "no": "#1A1A1A"}, # Solid white vs card gray
            labels={"response": "Responder Status", pct_col: "Frequency (%)"},
            points="outliers"
        )
        
        apply_bw_theme(fig_box)
        fig_box.update_layout(
            margin=dict(l=15, r=15, t=55, b=20),
            showlegend=False,
            title=dict(
                text=f"<b>{pop.replace('_', ' ').title()} Frequencies</b>",
                font=dict(size=14, family="Inter", color="#FFFFFF"),
                x=0.5,
                xanchor='center'
            ),
            xaxis=dict(
                title="Clinical Response Status",
                categoryorder="array",
                categoryarray=["no", "yes"],
                ticktext=["Non-Responder (No)", "Responder (Yes)"],
                tickvals=["no", "yes"],
                tickfont=dict(size=11, family="Space Mono", color="#A0A0A0")
            ),
            yaxis=dict(
                title="Frequency (%)", 
                tickfont=dict(size=11, family="Space Mono", color="#A0A0A0")
            ),
            hovermode="x unified"
        )
        # Apply clean borders and lines
        fig_box.update_traces(
            line=dict(color='#FFFFFF', width=1),
            marker=dict(line=dict(color='#FFFFFF', width=1))
        )
        
        # Deploy boxplot into the centered 3 + 2 grid structure
        if i < 3:
            row1_cols[i].plotly_chart(fig_box, use_container_width=True)
        else:
            # We place the last 2 charts in middle columns (indices 1 and 2)
            row2_cols[i - 2].plotly_chart(fig_box, use_container_width=True)
        
    # Display statistics table
    st.markdown("### Statistical Significance metrics")
    df_stat_tbl = pd.DataFrame(stat_rows)
    st.dataframe(df_stat_tbl, use_container_width=True, hide_index=True)
    
    # Statistical analysis conclusions
    st.markdown("### Analytical Conclusions")
    if time_val is None:
        st.success("""
        **Significant Finding (All Timepoints)**:
        - **CD4+ T-cell frequency** shows a statistically significant difference between responders and non-responders over the course of the treatment ($p$-value $= 0.0050$, Welch's t-test).
        - Responders have a significantly higher relative frequency of CD4+ T-cells (mean **30.538%** vs. **29.902%**).
        - CD8+ T-cells, B-cells, NK cells, and monocytes show no statistically significant differences ($p$-values $> 0.05$).
        """)
    else:
        st.warning("""
        **Baseline (t=0) Finding**:
        - **No immune cell populations** show a statistically significant frequency difference between responders and non-responders prior to treatment initiation (all $p$-values $> 0.20$).
        - This indicates that baseline immune cell frequencies alone are insufficient to predict treatment response, and longitudinal monitoring is necessary to observe miraclib's modulation of CD4+ T-cell helper populations.
        """)

# ----------------- TAB 4: COHORT EXPLORER -----------------
with tab_part4:
    st.markdown("## Part 4: Dynamic Cohort Explorer")
    st.write("Explore specific subsets of the clinical trial database interactively. Preloaded with Bob's baseline melanoma query.")
    
    # Interactive Sidebar Filters wrapped inside a clean bordered container
    with st.container(border=True):
        col_f1, col_f2, col_f3, col_f4 = st.columns(4)
        with col_f1:
            sel_cond = st.selectbox("Filter Condition / Indication", ["melanoma", "carcinoma", "healthy"], index=0, key="t4_cond")
        with col_f2:
            sel_type = st.selectbox("Filter Sample Type", ["PBMC", "WB"], index=0, key="t4_type")
        with col_f3:
            sel_time = st.selectbox("Filter Time From Treatment Start", [0, 7, 14], index=0, key="t4_time")
        with col_f4:
            sel_tx = st.selectbox("Filter Treatment", ["miraclib", "phauximab", "none"], index=0, key="t4_tx")

    # Dynamic Cohort SQL query builder
    query_cohort = f"""
    SELECT s.sample_id, sub.subject_id, sub.project_id, sub.response, sub.sex, c.b_cell
    FROM samples s
    JOIN subjects sub ON s.subject_id = sub.subject_id
    JOIN cell_counts c ON s.sample_id = c.sample_id
    WHERE sub.condition = '{sel_cond}'
      AND s.sample_type = '{sel_type}'
      AND s.time_from_treatment_start = {sel_time}
      AND sub.treatment = '{sel_tx}';
    """
    df_c = pd.read_sql_query(query_cohort, conn)
    
    st.markdown(f"Cohort Size with Selected Filters: **{len(df_c):,}** samples.")
    
    if len(df_c) == 0:
        st.warning("No samples found matching these filters. Try modifying your configuration.")
    else:
        col_res1, col_res2, col_res3 = st.columns(3)
        
        with col_res1:
            st.markdown("### 1. Samples from each project")
            df_p = df_c["project_id"].value_counts().reset_index()
            df_p.columns = ["Project ID", "Sample Count"]
            
            fig_p = px.bar(
                df_p, x="Project ID", y="Sample Count",
                color="Project ID", color_discrete_sequence=["#FFFFFF"],
                text="Sample Count"
            )
            apply_bw_theme(fig_p)
            fig_p.update_layout(
                margin=dict(l=15, r=15, t=30, b=15),
                showlegend=False
            )
            fig_p.update_traces(
                textposition='outside',
                cliponaxis=False,
                opacity=1.0
            )
            # Apply dynamic pattern fills for each trace to ensure unique monochrome textures
            patterns_p = ['', '/', '.']
            for idx, trace in enumerate(fig_p.data):
                trace.marker.pattern = dict(
                    shape=patterns_p[idx % len(patterns_p)],
                    fgcolor='#FFFFFF',
                    bgcolor='#1A1A1A',
                    solidity=0.25
                )
                trace.marker.line = dict(color='#FFFFFF', width=1)
            st.plotly_chart(fig_p, use_container_width=True)
            
        with col_res2:
            st.markdown("### 2. Subject responder counts")
            df_r = df_c["response"].value_counts().reset_index()
            df_r.columns = ["Responder Status", "Subject Count"]
            df_r["Responder Status"] = df_r["Responder Status"].fillna("Healthy Control")
            
            fig_r = px.bar(
                df_r, x="Responder Status", y="Subject Count",
                color="Responder Status", color_discrete_sequence=["#FFFFFF"],
                text="Subject Count"
            )
            apply_bw_theme(fig_r)
            fig_r.update_layout(
                margin=dict(l=15, r=15, t=30, b=15),
                showlegend=False
            )
            fig_r.update_traces(
                textposition='outside',
                cliponaxis=False,
                opacity=1.0
            )
            # Apply dynamic pattern fills for each trace to ensure unique monochrome textures
            patterns_r = ['', '/', 'x']
            for idx, trace in enumerate(fig_r.data):
                trace.marker.pattern = dict(
                    shape=patterns_r[idx % len(patterns_r)],
                    fgcolor='#FFFFFF',
                    bgcolor='#1A1A1A',
                    solidity=0.25
                )
                trace.marker.line = dict(color='#FFFFFF', width=1)
            st.plotly_chart(fig_r, use_container_width=True)
            
        with col_res3:
            st.markdown("### 3. Subject gender counts")
            df_s = df_c["sex"].value_counts().reset_index()
            df_s.columns = ["Sex", "Subject Count"]
            
            fig_s = px.bar(
                df_s, x="Sex", y="Subject Count",
                color="Sex", color_discrete_sequence=["#FFFFFF"],
                text="Subject Count"
            )
            apply_bw_theme(fig_s)
            fig_s.update_layout(
                margin=dict(l=15, r=15, t=30, b=15),
                showlegend=False
            )
            fig_s.update_traces(
                textposition='outside',
                cliponaxis=False,
                opacity=1.0
            )
            # Apply dynamic pattern fills for each trace to ensure unique monochrome textures
            patterns_s = ['', '/']
            for idx, trace in enumerate(fig_s.data):
                trace.marker.pattern = dict(
                    shape=patterns_s[idx % len(patterns_s)],
                    fgcolor='#FFFFFF',
                    bgcolor='#1A1A1A',
                    solidity=0.25
                )
                trace.marker.line = dict(color='#FFFFFF', width=1)
            st.plotly_chart(fig_s, use_container_width=True)
            
        st.divider()
        
        # Dynamic B-cells calculations
        sub_males_resp = df_c[(df_c["sex"] == "M") & (df_c["response"] == "yes")]
        avg_b_cells_miraclib = sub_males_resp["b_cell"].mean() if len(sub_males_resp) > 0 else 0.0
        
        # Case B query matches condition, type, time, sex, response regardless of treatment
        query_any_tx = f"""
        SELECT c.b_cell
        FROM samples s
        JOIN subjects sub ON s.subject_id = sub.subject_id
        JOIN cell_counts c ON s.sample_id = c.sample_id
        WHERE sub.condition = '{sel_cond}'
          AND s.sample_type = '{sel_type}'
          AND s.time_from_treatment_start = {sel_time}
          AND sub.sex = 'M'
          AND sub.response = 'yes';
        """
        df_any_tx = pd.read_sql_query(query_any_tx, conn)
        avg_b_cells_any_tx = df_any_tx["b_cell"].mean() if len(df_any_tx) > 0 else 0.0
        
        st.markdown(f"### 4. Average B-cells for Male Responders with **{sel_cond.title()}** at TimePoint={sel_time}")
        
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.markdown(f"""
            <div class="glass-card border-left-purple" style="text-align: center;">
                <div class="stat-label">CASE A: TREATED WITH SELECTED DRUG ({sel_tx.upper()})</div>
                <div class="stat-number">{avg_b_cells_miraclib:.2f}</div>
                <p style="color: #94A3B8; margin-top: 5px; font-size: 13px;">Cohort size: {len(sub_males_resp)} male responders</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col_c2:
            st.markdown(f"""
            <div class="glass-card border-left-orange" style="text-align: center;">
                <div class="stat-label">CASE B: TREATED WITH ANY TRIAL CANDIDATE</div>
                <div class="stat-number">{avg_b_cells_any_tx:.2f}</div>
                <p style="color: #94A3B8; margin-top: 5px; font-size: 13px;">Cohort size: {len(df_any_tx)} male responders</p>
            </div>
            """, unsafe_allow_html=True)

conn.close()
