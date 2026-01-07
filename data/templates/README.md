# Custom Data Collection Guide

This guide explains how to collect and load your **real company data** into the Neo4j Knowledge Base.

## 📁 Where to Put Your Data

All data files go in: `data/templates/`

## 📋 CSV Files to Fill Out

### 1. **employees.csv** - Your People
| Column | Required | Example | Notes |
|--------|----------|---------|-------|
| id | ✅ | EMP001 | Unique ID for each employee |
| name | ✅ | John Smith | Full name |
| email | ✅ | john@company.com | Unique email |
| title | ✅ | Software Engineer | Job title |
| department | ✅ | Engineering | Must match a department name |
| location | | San Francisco | Office location |
| hire_date | | 2023-01-15 | Format: YYYY-MM-DD |
| salary | | 95000 | Annual salary (number) |
| level | | Senior | Junior, Mid, Senior, Staff, Principal |
| bio | | Short description | Brief bio |
| phone | | +1-555-0101 | Phone number |

### 2. **departments.csv** - Your Departments
| Column | Required | Example |
|--------|----------|---------|
| name | ✅ | Engineering |
| description | | Software development team |

### 3. **projects.csv** - Your Projects
| Column | Required | Example | Notes |
|--------|----------|---------|-------|
| project_id | ✅ | PROJ001 | Unique project ID |
| name | ✅ | Mobile App | Project name |
| description | | App redesign | Brief description |
| status | ✅ | active | active, planning, on-hold, completed, cancelled |
| budget | | 250000 | Budget in dollars |
| priority | | high | low, medium, high, critical |
| start_date | | 2024-01-01 | Format: YYYY-MM-DD |
| end_date | | 2024-06-30 | Leave empty if ongoing |

### 4. **skills.csv** - Technical & Soft Skills
| Column | Required | Example |
|--------|----------|---------|
| name | ✅ | Python |
| category | | Programming |

**Common categories:** Programming, Frontend, Backend, Cloud, DevOps, Database, Data Science, Soft Skills

### 5. **clients.csv** - Your Clients
| Column | Required | Example |
|--------|----------|---------|
| id | ✅ | CLIENT001 |
| name | ✅ | Acme Corp |
| industry | | Technology |
| revenue | | 5000000 |
| contract_value | | 250000 |

---

## 🔗 Relationship Files

These connect your data together:

### 6. **employee_skills.csv** - Who knows what
```csv
employee_id,skill_name
EMP001,Python
EMP001,React
EMP002,Leadership
```

### 7. **employee_projects.csv** - Who works on what
```csv
employee_id,project_id,role
EMP001,PROJ001,Developer
EMP002,PROJ001,Product Owner
```

### 8. **project_clients.csv** - Projects for which clients
```csv
project_id,client_id
PROJ001,CLIENT001
```

### 9. **reporting_structure.csv** - Who reports to whom
```csv
employee_id,manager_id
EMP001,EMP003
```

---

## 🚀 How to Collect Data

### Option 1: Excel/Google Sheets
1. Open the CSV templates in Excel or Google Sheets
2. Fill in your data
3. Export as CSV (keep the same filename)
4. Save to `data/templates/`

### Option 2: Export from HR System
If you have an HRIS (Workday, BambooHR, etc.):
1. Export employee data as CSV
2. Map columns to match our template
3. Save as `employees.csv`

### Option 3: Manual Entry
1. Open CSV files in a text editor
2. Add rows following the existing format
3. Save the files

---

## ⚡ Loading Your Data

1. **Ensure your CSV files are in** `data/templates/`

2. **Activate your virtual environment:**
   ```bash
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Mac/Linux
   ```

3. **Run the loader:**
   ```bash
   python scripts/load_custom_data.py
   ```

4. **Confirm when prompted** (type `yes`)

5. **Verify in the app** at http://localhost:5173

---

## ⚠️ Important Notes

- **IDs must be unique** - Each employee, project, client needs a unique ID
- **Department names must match** - Employee's department must exist in departments.csv
- **Skill names are case-sensitive** - "Python" ≠ "python"
- **Dates format** - Use YYYY-MM-DD (e.g., 2024-01-15)
- **Numbers only for money** - No currency symbols (250000 not $250,000)

---

## 📊 Sample Data Flow

```
employees.csv ─────────────────┐
                               ├──> load_custom_data.py ──> Neo4j
departments.csv ───────────────┤
skills.csv ────────────────────┤
projects.csv ──────────────────┤
clients.csv ───────────────────┤
                               │
employee_skills.csv ───────────┤  (creates HAS_SKILL relationships)
employee_projects.csv ─────────┤  (creates WORKS_ON relationships)
project_clients.csv ───────────┤  (creates FOR_CLIENT relationships)
reporting_structure.csv ───────┘  (creates REPORTS_TO relationships)
```

---

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| "File not found" | Check CSV is in `data/templates/` with correct name |
| "No relationships created" | Verify IDs match between files |
| "Department not found" | Add department to departments.csv first |
| Connection error | Check `.env` has correct Neo4j credentials |

---

## 📞 Quick Start Checklist

- [ ] Fill out `departments.csv` first
- [ ] Fill out `skills.csv` 
- [ ] Fill out `employees.csv` (use department names from step 1)
- [ ] Fill out `projects.csv`
- [ ] Fill out `clients.csv` (if applicable)
- [ ] Fill out `employee_skills.csv` (connect employees to skills)
- [ ] Fill out `employee_projects.csv` (assign employees to projects)
- [ ] Run `python scripts/load_custom_data.py`
- [ ] Test queries in the app!
