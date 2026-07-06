# 🏛️ CivicPulse — Citizen Grievance Intelligence System
### Hackathon 2026 · Governance Analytics Platform

---

## 📋 Project Overview

**CivicPulse** is a full-stack Django + MongoDB analytics platform that transforms raw citizen grievance CSV data into an intelligent governance decision-support system. It surfaces systemic public service failures, benchmarks departmental efficiency, identifies high-risk regions, and generates data-driven recommendations — all through a premium dark-themed interactive dashboard.

---

## 🎯 Problem Statement

Local governance bodies receive thousands of citizen complaints but lack tools to:
- Identify recurring patterns and systemic failures
- Compare departmental performance objectively
- Detect high-risk regions before they escalate
- Generate actionable insights for resource allocation

**CivicPulse solves this with data-driven intelligence.**

---

## ⚡ Innovation Points

| Feature | Description |
|---------|-------------|
| **Efficiency Score** | Composite metric (40% resolution rate + 30% speed + 30% citizen rating) |
| **Risk Score** | Multi-factor regional risk (complaint density + unresolved rate + critical cases) |
| **Recurrence Score** | Category-level pattern detection for chronic issues |
| **Alert Engine** | Automated alerts for departments/regions exceeding thresholds |
| **Text Clustering** | Keyword extraction + theme grouping from complaint descriptions |
| **Graceful Fallback** | Runs without MongoDB (in-memory mode) — never crashes |
| **Filter API** | Real-time KPI refresh via REST endpoint with 5 filter dimensions |

---

## 🛠️ Tech Stack

```
Backend:      Python 3.11, Django 6.x
Database:     MongoDB (pymongo) + SQLite fallback
Analytics:    Pandas, NumPy
Charts:       Matplotlib (server-side PNG) + Chart.js (client-side interactive)
Frontend:     HTML5, CSS3, Vanilla JavaScript
Fonts:        Syne (headings), Space Grotesk (body), JetBrains Mono (code)
Icons:        Font Awesome 6.5
```

---

## 📁 Folder Structure

```
grievance_system/
├── data/
│   ├── grievance_data.csv          ← 2,000 complaint records (auto-generated)
│   └── generate_data.py            ← Dataset generator script
│
├── grievance_dashboard/
│   ├── analysis/
│   │   ├── __init__.py
│   │   └── engine.py               ← Core analytics engine (GrievanceEngine class)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── chart_service.py        ← Matplotlib chart generator (8 chart types)
│   │   └── mongo_service.py        ← MongoDB CRUD service with fallback
│   ├── templates/grievance_dashboard/
│   │   ├── base.html               ← Base layout (sidebar + topnav)
│   │   ├── home.html               ← Landing page with hero + feature cards
│   │   ├── dashboard.html          ← Main analytics dashboard
│   │   ├── department.html         ← Department performance analysis
│   │   ├── region.html             ← Regional risk analysis
│   │   ├── category.html           ← Complaint category breakdown
│   │   ├── text_insights.html      ← NLP keyword & theme analysis
│   │   ├── recommendations.html    ← AI-powered recommendations
│   │   ├── reports.html            ← Printable analytical report
│   │   ├── about.html              ← Project architecture & info
│   │   └── admin_panel.html        ← System status & API explorer
│   ├── views.py                    ← 10 page views + 4 REST API endpoints
│   ├── urls.py                     ← URL routing
│   └── apps.py
│
├── static/
│   └── charts/                     ← Generated PNG charts (auto-created)
│
├── grievance_system/
│   ├── settings.py                 ← Django config with MongoDB & CSV paths
│   ├── urls.py                     ← Root URL configuration
│   └── wsgi.py
│
├── manage.py
├── requirements.txt
└── README.md
```

---

## 📊 Sample CSV Format

```csv
complaint_id,citizen_id,department,region,category,severity,status,complaint_date,resolution_date,resolution_days,description,citizen_rating,mode_of_complaint,assigned_officer
GRV00001,CIT23434,Water Supply,North District,Water Shortage,High,Resolved,2022-03-15,2022-03-28,13,"No water supply for past 5 days in our area",4,Online Portal,Officer_115
GRV00002,CIT38893,Roads & Infrastructure,Old City,Road Damage,Critical,Pending,2023-07-20,,,,"Pothole on main road causing accidents near riverside",,,Mobile App,Officer_457
```

**Columns:**
- `complaint_id` — Unique identifier (GRV00001)
- `citizen_id` — Citizen identifier (CIT12345)
- `department` — Public department name
- `region` — District/zone name
- `category` — Complaint type
- `severity` — Low/Medium/High/Critical
- `status` — Resolved/Pending/In Progress/Closed/Reopened
- `complaint_date` — YYYY-MM-DD format
- `resolution_date` — YYYY-MM-DD (empty if unresolved)
- `resolution_days` — Days taken to resolve
- `description` — Free-text complaint description
- `citizen_rating` — 1–5 satisfaction rating (empty if unresolved)
- `mode_of_complaint` — Online Portal/Mobile App/Walk-in/Phone/Email
- `assigned_officer` — Officer ID

---

## 🚀 Step-by-Step Installation

### Prerequisites
- Python 3.10+
- pip
- MongoDB (optional — system runs without it)

### Step 1: Clone / Extract Project
```bash
cd grievance_system
```

### Step 2: Install Dependencies
```bash
pip install django pymongo pandas numpy matplotlib plotly
```

### Step 3: Generate Dataset
```bash
python data/generate_data.py
```
This creates `data/grievance_data.csv` with 2,000 realistic records.

### Step 4: Run Migrations
```bash
python manage.py migrate
```

### Step 5: Run the Server
```bash
python manage.py runserver
```

### Step 6: Open in Browser
```
http://127.0.0.1:8000/
```

> **MongoDB is optional.** If not installed/running, the system automatically falls back to in-memory mode with full functionality.

---

## 🌐 All Pages

| URL | Page | Description |
|-----|------|-------------|
| `/` | Home | Hero landing page with KPI strip |
| `/dashboard/` | Dashboard | Full analytics with 8+ charts |
| `/department/` | Departments | Efficiency scores & performance table |
| `/region/` | Regions | Risk heatmap & complaint distribution |
| `/category/` | Categories | Recurrence scores & delay analysis |
| `/text-insights/` | Text Insights | Keyword cloud & grievance themes |
| `/recommendations/` | Recommendations | AI alerts & action strategies |
| `/reports/` | Reports | Printable executive report |
| `/about/` | About | Architecture, modules & innovation |
| `/admin-panel/` | Admin | System health & API endpoints |

## 🔌 REST API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/kpis/` | GET | Summary KPI JSON |
| `/api/trend/` | GET | Monthly trend data |
| `/api/filtered/?department=X&region=Y&year=Z` | GET | Filtered KPIs |
| `/api/search/?q=water` | GET | Full-text search |

---

## 📈 Analytics Computed

### KPIs
- Total / Resolved / Pending complaints
- Resolution rate (%)
- Average resolution days
- Critical complaint count
- Citizen satisfaction rating

### Department Metrics
- Complaint volume
- Resolution rate
- Average resolution days
- Efficiency Score (composite)
- Speed Score
- Citizen Rating

### Region Metrics
- Total complaints
- Unresolved complaint rate
- Critical case count
- Risk Score (composite)

### Category Metrics
- Total complaints
- Resolution rate
- Average resolution days
- Recurrence Score

### Text Analysis
- Top 40 keywords from complaint descriptions
- 6 grievance theme clusters
- Dissatisfaction indicators

---

## 🗺️ System Architecture

```
[CSV File] ──────► [GrievanceEngine]
                        │
              ┌─────────┴──────────┐
              │                    │
         [Pandas EDA]        [Text Analysis]
              │                    │
         [MongoDB]           [ChartService]
              │                    │
         [Django Views] ◄──────────┘
              │
         [Templates + Chart.js]
              │
         [Browser Dashboard]
```

---
## 🔮 Future Enhancements

- LSTM time-series model for complaint spike prediction
- BERT-based sentiment analysis on complaint descriptions
- Leaflet.js GIS heatmap with real GPS coordinates
- Automated email/SMS alerts to department heads
- Citizen-facing mobile app with real-time tracking
- Blockchain audit trail for complaint resolution
- Multi-language support for regional languages
- Role-based access control (department officers vs. admin)

---

## 📦 Requirements

```
django>=4.2
pymongo>=4.0
pandas>=2.0
numpy>=1.24
matplotlib>=3.7
```

---

*Built for Hackathon 2024 · CivicPulse · Governance Intelligence Platform*
