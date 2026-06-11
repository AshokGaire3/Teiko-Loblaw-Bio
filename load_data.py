#!/usr/bin/env python3
import sqlite3
import csv
import os

DB_PATH = "teiko_clinical.db"
CSV_PATH = "cell-count.csv"

def init_db():
    print(f"Initializing SQLite database at: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Enable foreign keys support
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # Create projects table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        project_id TEXT PRIMARY KEY
    );
    """)
    
    # Create subjects table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS subjects (
        subject_id TEXT PRIMARY KEY,
        project_id TEXT,
        condition TEXT,
        age INTEGER,
        sex TEXT,
        treatment TEXT,
        response TEXT,
        FOREIGN KEY (project_id) REFERENCES projects(project_id)
    );
    """)
    
    # Create samples table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS samples (
        sample_id TEXT PRIMARY KEY,
        subject_id TEXT,
        sample_type TEXT,
        time_from_treatment_start INTEGER,
        FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
    );
    """)
    
    # Create cell_counts table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cell_counts (
        sample_id TEXT PRIMARY KEY,
        b_cell INTEGER,
        cd8_t_cell INTEGER,
        cd4_t_cell INTEGER,
        nk_cell INTEGER,
        monocyte INTEGER,
        FOREIGN KEY (sample_id) REFERENCES samples(sample_id)
    );
    """)
    
    conn.commit()
    conn.close()

def load_data():
    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(f"Source CSV data file not found at: {CSV_PATH}")
        
    print(f"Loading data from {CSV_PATH}...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Enable foreign keys support
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # Read the CSV and extract values
    projects = set()
    subjects = {}
    samples = []
    cell_counts = []
    
    with open(CSV_PATH, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            prj_id = row["project"]
            sbj_id = row["subject"]
            cond = row["condition"]
            age = int(row["age"]) if row["age"] else None
            sex = row["sex"]
            treatment = row["treatment"]
            
            # Handle empty values (e.g. response can be blank for healthy controls)
            response = row["response"]
            if response == "" or response.lower() == "nan":
                response = None
                
            sample_id = row["sample"]
            sample_type = row["sample_type"]
            time_start = int(row["time_from_treatment_start"])
            
            b_c = int(row["b_cell"])
            cd8 = int(row["cd8_t_cell"])
            cd4 = int(row["cd4_t_cell"])
            nk = int(row["nk_cell"])
            mono = int(row["monocyte"])
            
            # Add to sets/lists for relational insertion
            projects.add(prj_id)
            subjects[sbj_id] = (prj_id, cond, age, sex, treatment, response)
            samples.append((sample_id, sbj_id, sample_type, time_start))
            cell_counts.append((sample_id, b_c, cd8, cd4, nk, mono))
            
    # Insert Projects
    print(f"Inserting {len(projects)} projects...")
    cursor.executemany(
        "INSERT OR IGNORE INTO projects (project_id) VALUES (?);",
        [(p,) for p in projects]
    )
    
    # Insert Subjects
    print(f"Inserting {len(subjects)} subjects...")
    cursor.executemany(
        """
        INSERT OR IGNORE INTO subjects 
        (subject_id, project_id, condition, age, sex, treatment, response) 
        VALUES (?, ?, ?, ?, ?, ?, ?);
        """,
        [(s_id, *meta) for s_id, meta in subjects.items()]
    )
    
    # Insert Samples
    print(f"Inserting {len(samples)} samples...")
    cursor.executemany(
        """
        INSERT OR IGNORE INTO samples 
        (sample_id, subject_id, sample_type, time_from_treatment_start) 
        VALUES (?, ?, ?, ?);
        """,
        samples
    )
    
    # Insert Cell Counts
    print(f"Inserting cell count measurements...")
    cursor.executemany(
        """
        INSERT OR IGNORE INTO cell_counts 
        (sample_id, b_cell, cd8_t_cell, cd4_t_cell, nk_cell, monocyte) 
        VALUES (?, ?, ?, ?, ?, ?);
        """,
        cell_counts
    )
    
    conn.commit()
    
    # Verification query
    cursor.execute("SELECT COUNT(*) FROM projects;")
    n_projects = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM subjects;")
    n_subjects = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM samples;")
    n_samples = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM cell_counts;")
    n_counts = cursor.fetchone()[0]
    
    conn.close()
    
    print("\nDatabase loading summary:")
    print(f"  - Projects: {n_projects}")
    print(f"  - Subjects: {n_subjects}")
    print(f"  - Samples: {n_samples}")
    print(f"  - Cell Counts: {n_counts}")
    print("Database is fully populated!")

if __name__ == "__main__":
    init_db()
    load_data()
