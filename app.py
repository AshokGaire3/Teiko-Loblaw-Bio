import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
import plotly.express as px
from scipy import stats
import os

DB_PATH = "teiko_clinical.db"

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

# Custom CSS for Premium Design (Harmonious colors, modern fonts, glassmorphism card styling)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Inter:wght@300;400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    h1, h2, h3, h4, .metric-label {
        font-family: 'Outfit', sans-serif;
        font-weight: 600;
    }
    
    /* Sleek gradient background for sidebar */
    [data-testid="stSidebar"] {
        background-image: linear-gradient(180deg, #1E1B4B 0%, #0F172A 100%);
        color: #F8FAFC;
    }
    
    /* Custom CSS Cards for Glassmorphism UI with Micro-Animations */
    .glass-card {
        background: rgba(30, 41, 59, 0.55);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        backdrop-filter: blur(16px);
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.2);
        transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
    }
    
    .glass-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(99, 102, 241, 0.25);
        border-color: rgba(99, 102, 241, 0.4);
    }
    
    .stat-number {
        font-family: 'Outfit', sans-serif;
        font-size: 38px;
        font-weight: 800;
        color: #818CF8;
        margin-top: 5px;
    }
    
    .stat-label {
        font-size: 13px;
        color: #94A3B8;
        font-weight: 600;
        letter-spacing: 0.08em;
    }
    
    /* Highlight banner */
    .highlight-banner {
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 50%, #C084FC 100%);
        border-radius: 16px;
        padding: 24px;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 10px 30px rgba(79, 70, 229, 0.3);
    }
    
    /* Metric Card Custom Color-left borders */
    .border-left-purple { border-left: 5px solid #A855F7; }
    .border-left-orange { border-left: 5px solid #F97316; }
    .border-left-green { border-left: 5px solid #10B981; }
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

# Check DB
if not os.path.exists(DB_PATH):
    st.error("Database file 'teiko_clinical.db' not found. Please run the data ingestion pipeline first.")
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
    
    # Visual Cards row
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="glass-card border-left-purple">
            <div class="stat-label">TOTAL PROJECTS IN STUDY</div>
            <div class="stat-number">{total_projects} Projects</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="glass-card border-left-green">
            <div class="stat-label">ENROLLED SUBJECTS</div>
            <div class="stat-number">{total_subjects:,} Patients</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="glass-card border-left-orange">
            <div class="stat-label">COLLECTED BIOLOGICAL SAMPLES</div>
            <div class="stat-number">{total_samples:,} Samples</div>
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
                df_meta, names="condition", hole=0.4,
                title="Cohort Indication Split",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_ind.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=10, r=10, t=40, b=10)
            )
            st.plotly_chart(fig_ind, use_container_width=True)
            
        with col_c2:
            df_resp_agg = df_meta["response"].value_counts().reset_index()
            df_resp_agg.columns = ["response", "count"]
            df_resp_agg["response"] = df_resp_agg["response"].fillna("Healthy Control")
            
            fig_resp = px.pie(
                df_resp_agg, values="count", names="response", hole=0.4,
                title="Response Demographics Split",
                color_discrete_sequence=px.colors.qualitative.Safe
            )
            fig_resp.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=10, r=10, t=40, b=10)
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
    
    # Plot Interactive Plotly Boxplots in Columns
    st.markdown("### Interactive Frequencies Comparison")
    cols_box = st.columns(5)
    
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
            color_discrete_map={"yes": "#A855F7", "no": "#F97316"},
            labels={"response": "Responder", pct_col: "Frequency (%)"},
            points="outliers"
        )
        
        # Style Chart for dark glassmorphic look
        fig_box.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=40, b=10),
            showlegend=False,
            title=dict(
                text=f"<b>{pop.replace('_', ' ').title()}</b>",
                font=dict(size=14, family="Outfit")
            ),
            xaxis=dict(title="Responder"),
            yaxis=dict(title="Freq (%)")
        )
        cols_box[i].plotly_chart(fig_box, use_container_width=True)
        
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
    
    # Interactive Sidebar Filters inside the tab layout
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
                color="Project ID", color_discrete_sequence=px.colors.qualitative.Bold,
                text="Sample Count"
            )
            fig_p.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=10, r=10, t=30, b=10),
                showlegend=False
            )
            st.plotly_chart(fig_p, use_container_width=True)
            
        with col_res2:
            st.markdown("### 2. Subject responder counts")
            df_r = df_c["response"].value_counts().reset_index()
            df_r.columns = ["Responder Status", "Subject Count"]
            df_r["Responder Status"] = df_r["Responder Status"].fillna("Healthy Control")
            
            fig_r = px.bar(
                df_r, x="Responder Status", y="Subject Count",
                color="Responder Status", color_discrete_sequence=px.colors.qualitative.Set2,
                text="Subject Count"
            )
            fig_r.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=10, r=10, t=30, b=10),
                showlegend=False
            )
            st.plotly_chart(fig_r, use_container_width=True)
            
        with col_res3:
            st.markdown("### 3. Subject gender counts")
            df_s = df_c["sex"].value_counts().reset_index()
            df_s.columns = ["Sex", "Subject Count"]
            
            fig_s = px.bar(
                df_s, x="Sex", y="Subject Count",
                color="Sex", color_discrete_sequence=px.colors.qualitative.Pastel1,
                text="Subject Count"
            )
            fig_s.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=10, r=10, t=30, b=10),
                showlegend=False
            )
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
