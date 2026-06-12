#!/usr/bin/env python3
import os
import sqlite3
import pandas as pd

DB_PATH = "teiko_clinical.db"
OUTPUT_DIR = "output"

def verify_all():
    print("--- Running Automated Ingestion & Pipeline Verification ---")
    
    # 1. Check SQLite Database File
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Missing database file: {DB_PATH}")
    print(f"✓ Found database: {DB_PATH}")
    
    # 2. Check Database Tables and Counts
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    tables = ["projects", "subjects", "samples", "cell_counts"]
    for t in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {t};")
        count = cursor.fetchone()[0]
        print(f"✓ Table '{t}' exists. Rows: {count}")
        if count == 0:
            raise ValueError(f"Table '{t}' has 0 rows.")
            
    # Verify exact counts
    cursor.execute("SELECT COUNT(*) FROM samples;")
    n_samples = cursor.fetchone()[0]
    if n_samples != 10500:
        raise ValueError(f"Expected 10500 samples, found {n_samples}")
    
    cursor.execute("SELECT COUNT(*) FROM subjects;")
    n_subjects = cursor.fetchone()[0]
    if n_subjects != 3500:
        raise ValueError(f"Expected 3500 subjects, found {n_subjects}")
        
    conn.close()
    
    # 3. Check Part 2 Output Table
    p2_csv = os.path.join(OUTPUT_DIR, "initial_analysis_summary.csv")
    if not os.path.exists(p2_csv):
        raise FileNotFoundError(f"Missing Part 2 summary table: {p2_csv}")
    print(f"✓ Found initial summary CSV: {p2_csv}")
    
    df_p2 = pd.read_csv(p2_csv)
    expected_cols = ["sample", "total_count", "population", "count", "percentage"]
    for col in expected_cols:
        if col not in df_p2.columns:
            raise KeyError(f"Missing column '{col}' in Part 2 summary table.")
    if len(df_p2) != 52500:
        raise ValueError(f"Expected 52500 rows in Part 2 summary, found {len(df_p2)}")
    print(f"✓ Part 2 CSV format verified successfully (52,500 rows).")
    
    # 4. Check Part 3 Outputs
    p3_plot = os.path.join(OUTPUT_DIR, "responders_vs_nonresponders_boxplots.png")
    p3_report = os.path.join(OUTPUT_DIR, "statistical_analysis_report.md")
    if not os.path.exists(p3_plot):
        raise FileNotFoundError(f"Missing boxplot image: {p3_plot}")
    if not os.path.exists(p3_report):
        raise FileNotFoundError(f"Missing statistical analysis report: {p3_report}")
    print(f"✓ Found boxplot visualization: {p3_plot}")
    print(f"✓ Found statistical report: {p3_report}")
    
    # 5. Check Part 4 Output
    p4_report = os.path.join(OUTPUT_DIR, "subset_analysis_report.md")
    if not os.path.exists(p4_report):
        raise FileNotFoundError(f"Missing subset analysis report: {p4_report}")
    print(f"✓ Found subset analysis report: {p4_report}")
    
    # Check that average values are reported correctly
    with open(p4_report, "r", encoding="utf-8") as f:
        content = f.read()
        if "10401.28" not in content:
            raise ValueError("Part 4 B-cell average Case A (10401.28) not found in report.")
        if "10206.72" not in content:
            raise ValueError("Part 4 B-cell average Case B (10206.72) not found in report.")
    print("✓ Part 4 B-cell answers verified successfully.")
    
    print("\n🎉 Verification Successful! All deliverables generated and compliant.")

if __name__ == "__main__":
    try:
        verify_all()
    except Exception as e:
        print(f"\n❌ Verification Failed: {e}")
        exit(1)
