"""
Grievance Analytics Engine
Core data processing, cleaning, and analysis module
"""

import pandas as pd
import numpy as np
from pathlib import Path
import re
from collections import Counter
import warnings
warnings.filterwarnings('ignore')


class GrievanceEngine:
    """Main analytics engine for citizen grievance data"""

    def __init__(self, csv_path: str):
        self.csv_path = Path(csv_path)
        self.df_raw = None
        self.df = None
        self._loaded = False

    # ─────────────────────────────────────────
    # 1. DATA INGESTION
    # ─────────────────────────────────────────
    def load_data(self):
        if not self.csv_path.exists():
            raise FileNotFoundError(f"Dataset not found at {self.csv_path}")

        self.df_raw = pd.read_csv(self.csv_path, low_memory=False)
        self.df = self.df_raw.copy()
        self._loaded = True
        return self

    def _ensure_loaded(self):
        if not self._loaded:
            self.load_data()

    # ─────────────────────────────────────────
    # 2. DATA CLEANING
    # ─────────────────────────────────────────
    def clean_data(self):
        self._ensure_loaded()
        df = self.df.copy()

        # Standardize column names
        df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]

        # Drop duplicates
        df.drop_duplicates(subset=['complaint_id'], inplace=True)

        # Normalize text fields
        for col in ['department', 'region', 'category', 'status', 'severity']:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip().str.title()

        # Parse dates
        df['complaint_date'] = pd.to_datetime(df['complaint_date'], errors='coerce')
        df['resolution_date'] = pd.to_datetime(df['resolution_date'], errors='coerce')

        # Drop rows with no complaint date
        df.dropna(subset=['complaint_date'], inplace=True)

        # Derived fields
        df['complaint_month'] = df['complaint_date'].dt.month
        df['complaint_year'] = df['complaint_date'].dt.year
        df['complaint_month_name'] = df['complaint_date'].dt.strftime('%b %Y')
        df['complaint_quarter'] = df['complaint_date'].dt.to_period('Q').astype(str)

        # Resolution days (recalculate from dates when possible)
        mask_resolved = df['resolution_date'].notna()
        df.loc[mask_resolved, 'resolution_days'] = (
            df.loc[mask_resolved, 'resolution_date'] - df.loc[mask_resolved, 'complaint_date']
        ).dt.days

        # Fill numeric
        df['resolution_days'] = pd.to_numeric(df['resolution_days'], errors='coerce')
        df['citizen_rating'] = pd.to_numeric(df['citizen_rating'], errors='coerce')

        # Resolution status flag
        df['is_resolved'] = df['status'].isin(['Resolved', 'Closed'])
        df['is_pending'] = df['status'].isin(['Pending', 'In Progress', 'Reopened'])

        # Clean description
        df['description'] = df['description'].fillna('No description provided').astype(str)

        self.df = df
        return self

    # ─────────────────────────────────────────
    # 3. EXPLORATORY DATA ANALYSIS
    # ─────────────────────────────────────────
    def get_summary_kpis(self) -> dict:
        df = self.df
        total = len(df)
        resolved = df['is_resolved'].sum()
        pending = df['is_pending'].sum()
        avg_res = df.loc[df['is_resolved'], 'resolution_days'].mean()
        avg_rating = df['citizen_rating'].mean()
        critical = (df['severity'] == 'Critical').sum()

        return {
            'total_complaints': int(total),
            'resolved': int(resolved),
            'pending': int(pending),
            'resolution_rate': round(resolved / total * 100, 1) if total else 0,
            'avg_resolution_days': round(float(avg_res), 1) if not np.isnan(avg_res) else 0,
            'avg_citizen_rating': round(float(avg_rating), 2) if not np.isnan(avg_rating) else 0,
            'critical_complaints': int(critical),
            'departments_count': df['department'].nunique(),
            'regions_count': df['region'].nunique(),
            'categories_count': df['category'].nunique(),
        }

    def get_department_analysis(self) -> pd.DataFrame:
        df = self.df
        grp = df.groupby('department').agg(
            total=('complaint_id', 'count'),
            resolved=('is_resolved', 'sum'),
            pending=('is_pending', 'sum'),
            avg_resolution_days=('resolution_days', 'mean'),
            avg_rating=('citizen_rating', 'mean'),
            critical=('severity', lambda x: (x == 'Critical').sum()),
        ).reset_index()
        grp['resolution_rate'] = (grp['resolved'] / grp['total'] * 100).round(1)
        grp['avg_resolution_days'] = grp['avg_resolution_days'].round(1).fillna(0)
        grp['avg_rating'] = grp['avg_rating'].round(2).fillna(0)
        # Efficiency score: 40% resolution rate + 30% speed + 30% rating
        max_days = grp['avg_resolution_days'].replace(0, np.nan).max()
        grp['speed_score'] = (1 - grp['avg_resolution_days'] / (max_days + 1)) * 100
        grp['efficiency_score'] = (
            grp['resolution_rate'] * 0.4 +
            grp['speed_score'] * 0.3 +
            (grp['avg_rating'] / 5 * 100) * 0.3
        ).round(1)
        return grp.sort_values('total', ascending=False)

    def get_region_analysis(self) -> pd.DataFrame:
        df = self.df
        grp = df.groupby('region').agg(
            total=('complaint_id', 'count'),
            resolved=('is_resolved', 'sum'),
            pending=('is_pending', 'sum'),
            critical=('severity', lambda x: (x == 'Critical').sum()),
            avg_resolution_days=('resolution_days', 'mean'),
        ).reset_index()
        grp['resolution_rate'] = (grp['resolved'] / grp['total'] * 100).round(1)
        grp['unresolved_rate'] = (100 - grp['resolution_rate']).round(1)
        grp['avg_resolution_days'] = grp['avg_resolution_days'].round(1).fillna(0)
        # Risk score: complaint density + unresolved + critical
        max_total = grp['total'].max()
        grp['risk_score'] = (
            (grp['total'] / max_total * 40) +
            (grp['unresolved_rate'] / 100 * 35) +
            (grp['critical'] / grp['total'] * 25)
        ).round(1)
        return grp.sort_values('total', ascending=False)

    def get_category_analysis(self) -> pd.DataFrame:
        df = self.df
        grp = df.groupby('category').agg(
            total=('complaint_id', 'count'),
            resolved=('is_resolved', 'sum'),
            avg_resolution_days=('resolution_days', 'mean'),
            critical=('severity', lambda x: (x == 'Critical').sum()),
        ).reset_index()
        grp['resolution_rate'] = (grp['resolved'] / grp['total'] * 100).round(1)
        grp['avg_resolution_days'] = grp['avg_resolution_days'].round(1).fillna(0)
        grp['recurrence_score'] = (grp['total'] / grp['total'].max() * 100).round(1)
        return grp.sort_values('total', ascending=False)

    def get_trend_data(self) -> dict:
        df = self.df.copy()
        df['month_period'] = df['complaint_date'].dt.to_period('M')
        trend = df.groupby('month_period').agg(
            total=('complaint_id', 'count'),
            resolved=('is_resolved', 'sum'),
        ).reset_index()
        trend['month_str'] = trend['month_period'].astype(str)
        trend['pending'] = trend['total'] - trend['resolved']
        return {
            'labels': trend['month_str'].tolist(),
            'total': trend['total'].tolist(),
            'resolved': trend['resolved'].tolist(),
            'pending': trend['pending'].tolist(),
        }

    def get_severity_distribution(self) -> dict:
        counts = self.df['severity'].value_counts()
        return {'labels': counts.index.tolist(), 'values': counts.values.tolist()}

    def get_status_distribution(self) -> dict:
        counts = self.df['status'].value_counts()
        return {'labels': counts.index.tolist(), 'values': counts.values.tolist()}

    def get_monthly_growth(self) -> dict:
        df = self.df.copy()
        df['ym'] = df['complaint_date'].dt.strftime('%Y-%m')
        monthly = df.groupby('ym').size().reset_index(name='count')
        monthly['growth'] = monthly['count'].pct_change().fillna(0).round(3) * 100
        return {
            'labels': monthly['ym'].tolist(),
            'counts': monthly['count'].tolist(),
            'growth': monthly['growth'].tolist(),
        }

    # ─────────────────────────────────────────
    # 4. TEXT ANALYSIS
    # ─────────────────────────────────────────
    STOP_WORDS = {
        'the', 'a', 'an', 'is', 'in', 'on', 'at', 'to', 'for', 'of', 'and',
        'our', 'our', 'this', 'that', 'has', 'have', 'been', 'are', 'was',
        'were', 'with', 'from', 'not', 'no', 'by', 'be', 'it', 'its',
        'we', 'they', 'their', 'since', 'after', 'causing', 'near',
        'complaint', 'issue', 'problem', 'area', 'locality', 'affecting'
    }

    def get_keyword_frequencies(self, top_n: int = 30) -> list:
        texts = self.df['description'].str.lower()
        words = []
        for t in texts:
            tokens = re.findall(r'\b[a-z]{4,}\b', t)
            words.extend([w for w in tokens if w not in self.STOP_WORDS])
        counter = Counter(words)
        return [{'word': w, 'count': c} for w, c in counter.most_common(top_n)]

    def get_grievance_themes(self) -> list:
        """Group complaints into broad themes"""
        theme_map = {
            'Water & Sanitation': ['water', 'drain', 'sewage', 'pipeline', 'sanitation', 'garbage'],
            'Roads & Transport': ['road', 'pothole', 'street', 'transport', 'bus', 'vehicle'],
            'Energy & Utilities': ['electricity', 'power', 'light', 'transformer', 'outage'],
            'Health & Safety': ['health', 'hospital', 'mosquito', 'pollution', 'disease'],
            'Administration': ['documentation', 'corruption', 'tax', 'officer', 'delayed'],
            'Housing & Land': ['encroachment', 'construction', 'housing', 'property', 'land'],
        }
        df = self.df.copy()
        desc_lower = df['description'].str.lower()
        result = []
        for theme, keywords in theme_map.items():
            mask = desc_lower.apply(lambda x: any(k in x for k in keywords))
            count = mask.sum()
            result.append({'theme': theme, 'count': int(count),
                           'percentage': round(count / len(df) * 100, 1)})
        return sorted(result, key=lambda x: x['count'], reverse=True)

    # ─────────────────────────────────────────
    # 5. SMART INSIGHTS
    # ─────────────────────────────────────────
    def generate_insights(self) -> dict:
        dept_df = self.get_department_analysis()
        region_df = self.get_region_analysis()
        cat_df = self.get_category_analysis()
        kpis = self.get_summary_kpis()

        # Top 5 complaint-heavy departments
        top_depts = dept_df.nlargest(5, 'total')[['department', 'total', 'resolution_rate']].to_dict('records')

        # Worst performing departments (lowest efficiency)
        worst_depts = dept_df.nsmallest(5, 'efficiency_score')[['department', 'efficiency_score', 'resolution_rate']].to_dict('records')

        # Slowest resolution departments
        slow_depts = dept_df[dept_df['avg_resolution_days'] > 0].nlargest(5, 'avg_resolution_days')[
            ['department', 'avg_resolution_days']].to_dict('records')

        # High risk regions
        top_risk = region_df.nlargest(5, 'risk_score')[['region', 'risk_score', 'total', 'unresolved_rate']].to_dict('records')

        # High unresolved regions
        high_unres = region_df.nlargest(5, 'unresolved_rate')[['region', 'unresolved_rate', 'total']].to_dict('records')

        # Most recurring categories
        top_cats = cat_df.nlargest(5, 'total')[['category', 'total', 'avg_resolution_days']].to_dict('records')

        # Alerts
        alerts = []
        for _, row in region_df.iterrows():
            if row['unresolved_rate'] > 60:
                alerts.append({
                    'type': 'danger',
                    'icon': '🚨',
                    'message': f"{row['region']} has {row['unresolved_rate']}% unresolved complaints — immediate action needed."
                })
        for _, row in dept_df.iterrows():
            if row['avg_resolution_days'] > 40 and row['total'] > 50:
                alerts.append({
                    'type': 'warning',
                    'icon': '⚠️',
                    'message': f"{row['department']} averages {row['avg_resolution_days']} days to resolve — far above acceptable limits."
                })
        for _, row in cat_df.iterrows():
            if row['recurrence_score'] > 80:
                alerts.append({
                    'type': 'info',
                    'icon': '🔁',
                    'message': f"'{row['category']}' is the most recurring complaint type with {row['total']} occurrences."
                })
        alerts = alerts[:8]

        # Recommendations
        recommendations = [
            {
                'priority': 'High',
                'icon': '💧',
                'title': 'Strengthen Water Infrastructure',
                'description': 'Water-related complaints dominate records. Deploy rapid-response maintenance teams in high-density zones.'
            },
            {
                'priority': 'High',
                'icon': '🛣️',
                'title': 'Road Repair Prioritization',
                'description': 'Implement a real-time pothole reporting and repair tracking system tied to GPS data.'
            },
            {
                'priority': 'Medium',
                'icon': '⚡',
                'title': 'Power Grid Modernization',
                'description': 'Partner with electricity board for smart grid deployment in top 3 outage-prone regions.'
            },
            {
                'priority': 'Medium',
                'icon': '📊',
                'title': 'Department Performance Dashboards',
                'description': 'Mandate weekly KPI reviews for departments with efficiency scores below 50%.'
            },
            {
                'priority': 'Low',
                'icon': '📱',
                'title': 'Mobile Grievance Platform',
                'description': 'Expand mobile app adoption for faster complaint submission and real-time status tracking.'
            },
            {
                'priority': 'High',
                'icon': '🎯',
                'title': 'SLA Enforcement',
                'description': f"Enforce 15-day resolution SLA. Current average is {kpis['avg_resolution_days']} days."
            },
        ]

        return {
            'kpis': kpis,
            'top_complaint_departments': top_depts,
            'worst_performing_departments': worst_depts,
            'slowest_departments': slow_depts,
            'high_risk_regions': top_risk,
            'high_unresolved_regions': high_unres,
            'top_categories': top_cats,
            'alerts': alerts,
            'recommendations': recommendations,
        }

    def get_mode_distribution(self) -> dict:
        counts = self.df['mode_of_complaint'].value_counts()
        return {'labels': counts.index.tolist(), 'values': counts.values.tolist()}

    def get_yearly_comparison(self) -> dict:
        df = self.df.copy()
        yearly = df.groupby('complaint_year').agg(
            total=('complaint_id', 'count'),
            resolved=('is_resolved', 'sum'),
        ).reset_index()
        yearly['pending'] = yearly['total'] - yearly['resolved']
        return {
            'years': yearly['complaint_year'].astype(str).tolist(),
            'total': yearly['total'].tolist(),
            'resolved': yearly['resolved'].tolist(),
            'pending': yearly['pending'].tolist(),
        }

    def get_department_trend(self, dept: str) -> dict:
        df = self.df[self.df['department'] == dept].copy()
        df['ym'] = df['complaint_date'].dt.strftime('%Y-%m')
        trend = df.groupby('ym').size().reset_index(name='count')
        return {'labels': trend['ym'].tolist(), 'counts': trend['count'].tolist()}

    def get_filtered_data(self, department=None, region=None, category=None,
                          year=None, severity=None) -> pd.DataFrame:
        df = self.df.copy()
        if department and department != 'All':
            df = df[df['department'] == department]
        if region and region != 'All':
            df = df[df['region'] == region]
        if category and category != 'All':
            df = df[df['category'] == category]
        if year and year != 'All':
            df = df[df['complaint_year'] == int(year)]
        if severity and severity != 'All':
            df = df[df['severity'] == severity]
        return df

    def get_unique_values(self) -> dict:
        return {
            'departments': sorted(self.df['department'].unique().tolist()),
            'regions': sorted(self.df['region'].unique().tolist()),
            'categories': sorted(self.df['category'].unique().tolist()),
            'years': sorted(self.df['complaint_year'].unique().tolist()),
            'severities': sorted(self.df['severity'].unique().tolist()),
        }
