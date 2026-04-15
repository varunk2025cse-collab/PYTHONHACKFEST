"""
Chart Generation Service
Generates Matplotlib charts and saves them as PNG files
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path
import os

# Color palette
COLORS = {
    'primary': '#6366f1',
    'secondary': '#8b5cf6',
    'accent': '#06b6d4',
    'success': '#10b981',
    'warning': '#f59e0b',
    'danger': '#ef4444',
    'dark': '#1e1b4b',
    'bg': '#0f0e17',
    'card': '#1a1a2e',
    'text': '#e2e8f0',
}

PALETTE = ['#6366f1', '#8b5cf6', '#06b6d4', '#10b981', '#f59e0b',
           '#ef4444', '#ec4899', '#14b8a6', '#f97316', '#84cc16']


def _setup_dark_style():
    plt.rcParams.update({
        'figure.facecolor': '#0f0e17',
        'axes.facecolor': '#1a1a2e',
        'axes.edgecolor': '#334155',
        'axes.labelcolor': '#94a3b8',
        'text.color': '#e2e8f0',
        'xtick.color': '#94a3b8',
        'ytick.color': '#94a3b8',
        'grid.color': '#1e293b',
        'grid.alpha': 0.4,
        'font.family': 'DejaVu Sans',
        'font.size': 9,
    })


def save_chart(fig, name: str, chart_dir: str) -> str:
    path = Path(chart_dir) / f"{name}.png"
    fig.savefig(path, dpi=120, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    return f"/static/charts/{name}.png"


def generate_trend_chart(trend_data: dict, chart_dir: str) -> str:
    _setup_dark_style()
    fig, ax = plt.subplots(figsize=(12, 4))
    labels = trend_data['labels']
    x = range(len(labels))

    ax.fill_between(x, trend_data['total'], alpha=0.15, color=COLORS['primary'])
    ax.plot(x, trend_data['total'], color=COLORS['primary'], linewidth=2.5, label='Total', marker='o', markersize=3)
    ax.fill_between(x, trend_data['resolved'], alpha=0.1, color=COLORS['success'])
    ax.plot(x, trend_data['resolved'], color=COLORS['success'], linewidth=2, label='Resolved', linestyle='--')
    ax.plot(x, trend_data['pending'], color=COLORS['warning'], linewidth=2, label='Pending', linestyle=':')

    # X-axis labels (sparse)
    step = max(1, len(labels) // 12)
    ax.set_xticks(list(x)[::step])
    ax.set_xticklabels(labels[::step], rotation=45, ha='right', fontsize=7)
    ax.set_ylabel('Complaints', fontsize=9)
    ax.set_title('Complaint Trend Over Time', fontsize=12, fontweight='bold', color='white', pad=12)
    ax.legend(loc='upper left', fontsize=8, framealpha=0.3)
    ax.grid(True, axis='y')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    return save_chart(fig, 'trend_chart', chart_dir)


def generate_dept_bar_chart(dept_df, chart_dir: str) -> str:
    _setup_dark_style()
    top = dept_df.head(10)
    fig, ax = plt.subplots(figsize=(11, 5))
    bars = ax.barh(top['department'], top['total'], color=PALETTE[:len(top)], edgecolor='none', height=0.65)
    for bar in bars:
        w = bar.get_width()
        ax.text(w + 1, bar.get_y() + bar.get_height() / 2, str(int(w)),
                va='center', ha='left', fontsize=8, color='#94a3b8')
    ax.set_xlabel('Number of Complaints', fontsize=9)
    ax.set_title('Department-wise Complaint Volume', fontsize=12, fontweight='bold', color='white', pad=12)
    ax.invert_yaxis()
    ax.grid(True, axis='x', alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    return save_chart(fig, 'dept_bar_chart', chart_dir)


def generate_category_pie_chart(cat_df, chart_dir: str) -> str:
    _setup_dark_style()
    top = cat_df.head(8)
    other = cat_df.iloc[8:]['total'].sum()
    labels = top['category'].tolist()
    values = top['total'].tolist()
    if other > 0:
        labels.append('Others')
        values.append(int(other))

    fig, ax = plt.subplots(figsize=(9, 7))
    wedges, texts, autotexts = ax.pie(
        values, labels=None, autopct='%1.1f%%',
        colors=PALETTE[:len(values)], startangle=140,
        pctdistance=0.82, wedgeprops=dict(edgecolor='#0f0e17', linewidth=2)
    )
    for t in autotexts:
        t.set_fontsize(8)
        t.set_color('white')

    ax.legend(wedges, labels, title="Categories", loc="center left",
              bbox_to_anchor=(1, 0, 0.5, 1), fontsize=8, framealpha=0.2)
    ax.set_title('Complaint Category Distribution', fontsize=12, fontweight='bold', color='white', pad=12)
    return save_chart(fig, 'category_pie_chart', chart_dir)


def generate_resolution_time_chart(dept_df, chart_dir: str) -> str:
    _setup_dark_style()
    df = dept_df[dept_df['avg_resolution_days'] > 0].sort_values('avg_resolution_days', ascending=False).head(10)
    fig, ax = plt.subplots(figsize=(11, 5))
    colors = [COLORS['danger'] if v > 30 else COLORS['warning'] if v > 15 else COLORS['success']
              for v in df['avg_resolution_days']]
    bars = ax.barh(df['department'], df['avg_resolution_days'], color=colors, edgecolor='none', height=0.65)
    ax.axvline(x=15, color='#06b6d4', linestyle='--', alpha=0.7, linewidth=1.5, label='SLA: 15 days')
    for bar in bars:
        w = bar.get_width()
        ax.text(w + 0.3, bar.get_y() + bar.get_height() / 2, f'{w:.1f}d',
                va='center', ha='left', fontsize=8, color='#94a3b8')
    ax.set_xlabel('Avg Resolution Days', fontsize=9)
    ax.set_title('Average Resolution Time by Department', fontsize=12, fontweight='bold', color='white', pad=12)
    ax.legend(fontsize=8, framealpha=0.3)
    ax.invert_yaxis()
    ax.grid(True, axis='x', alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    return save_chart(fig, 'resolution_time_chart', chart_dir)


def generate_region_chart(region_df, chart_dir: str) -> str:
    _setup_dark_style()
    top = region_df.head(10)
    x = np.arange(len(top))
    width = 0.35
    fig, ax = plt.subplots(figsize=(12, 5))
    b1 = ax.bar(x - width / 2, top['resolved'], width, label='Resolved', color=COLORS['success'], alpha=0.85)
    b2 = ax.bar(x + width / 2, top['pending'], width, label='Pending', color=COLORS['danger'], alpha=0.85)
    ax.set_xticks(x)
    ax.set_xticklabels(top['region'], rotation=35, ha='right', fontsize=8)
    ax.set_ylabel('Complaints', fontsize=9)
    ax.set_title('Region-wise Resolved vs Pending Complaints', fontsize=12, fontweight='bold', color='white', pad=12)
    ax.legend(fontsize=9, framealpha=0.3)
    ax.grid(True, axis='y', alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    return save_chart(fig, 'region_chart', chart_dir)


def generate_efficiency_radar_chart(dept_df, chart_dir: str) -> str:
    _setup_dark_style()
    top5 = dept_df.nlargest(5, 'efficiency_score')
    categories = ['Efficiency\nScore', 'Resolution\nRate', 'Speed\nScore', 'Avg Rating\n(×20)']

    fig, ax = plt.subplots(figsize=(9, 6))
    bar_width = 0.15
    x = np.arange(len(categories))

    for i, (_, row) in enumerate(top5.iterrows()):
        vals = [
            row.get('efficiency_score', 0),
            row.get('resolution_rate', 0),
            row.get('speed_score', 0),
            row.get('avg_rating', 0) * 20,
        ]
        ax.bar(x + i * bar_width, vals, bar_width, label=row['department'][:15],
               color=PALETTE[i % len(PALETTE)], alpha=0.85)

    ax.set_xticks(x + bar_width * 2)
    ax.set_xticklabels(categories, fontsize=9)
    ax.set_ylabel('Score', fontsize=9)
    ax.set_title('Top 5 Department Performance Comparison', fontsize=12, fontweight='bold', color='white', pad=12)
    ax.legend(fontsize=7, framealpha=0.3, loc='upper right')
    ax.grid(True, axis='y', alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    return save_chart(fig, 'efficiency_chart', chart_dir)


def generate_monthly_growth_chart(growth_data: dict, chart_dir: str) -> str:
    _setup_dark_style()
    labels = growth_data['labels']
    counts = growth_data['counts']
    growth = growth_data['growth']
    x = range(len(labels))

    fig, ax1 = plt.subplots(figsize=(12, 4))
    ax2 = ax1.twinx()

    ax1.bar(x, counts, color=COLORS['primary'], alpha=0.6, label='Complaints')
    ax2.plot(x, growth, color=COLORS['accent'], linewidth=2, label='Growth %', marker='o', markersize=3)
    ax2.axhline(0, color='#ef4444', linestyle='--', alpha=0.5, linewidth=1)

    step = max(1, len(labels) // 12)
    ax1.set_xticks(list(x)[::step])
    ax1.set_xticklabels(labels[::step], rotation=45, ha='right', fontsize=7)
    ax1.set_ylabel('Complaints', fontsize=9)
    ax2.set_ylabel('Growth %', fontsize=9, color=COLORS['accent'])

    ax1.set_title('Monthly Complaint Volume & Growth Rate', fontsize=12, fontweight='bold', color='white', pad=12)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, fontsize=8, framealpha=0.3)
    ax1.grid(True, axis='y', alpha=0.2)
    ax1.spines['top'].set_visible(False)

    return save_chart(fig, 'monthly_growth_chart', chart_dir)


def generate_severity_chart(severity_data: dict, chart_dir: str) -> str:
    _setup_dark_style()
    labels = severity_data['labels']
    values = severity_data['values']
    sev_colors = {'Critical': '#ef4444', 'High': '#f59e0b', 'Medium': '#6366f1', 'Low': '#10b981'}
    colors = [sev_colors.get(l, '#94a3b8') for l in labels]

    fig, ax = plt.subplots(figsize=(7, 5))
    bars = ax.bar(labels, values, color=colors, edgecolor='none', width=0.55)
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h + 1, str(int(h)),
                ha='center', va='bottom', fontsize=10, fontweight='bold', color='white')
    ax.set_xlabel('Severity Level', fontsize=9)
    ax.set_ylabel('Count', fontsize=9)
    ax.set_title('Complaint Severity Distribution', fontsize=12, fontweight='bold', color='white', pad=12)
    ax.grid(True, axis='y', alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    return save_chart(fig, 'severity_chart', chart_dir)


def generate_all_charts(engine, chart_dir: str) -> dict:
    """Generate all charts and return URL mapping"""
    os.makedirs(chart_dir, exist_ok=True)
    dept_df = engine.get_department_analysis()
    region_df = engine.get_region_analysis()
    cat_df = engine.get_category_analysis()

    return {
        'trend': generate_trend_chart(engine.get_trend_data(), chart_dir),
        'dept_bar': generate_dept_bar_chart(dept_df, chart_dir),
        'category_pie': generate_category_pie_chart(cat_df, chart_dir),
        'resolution_time': generate_resolution_time_chart(dept_df, chart_dir),
        'region': generate_region_chart(region_df, chart_dir),
        'efficiency': generate_efficiency_radar_chart(dept_df, chart_dir),
        'monthly_growth': generate_monthly_growth_chart(engine.get_monthly_growth(), chart_dir),
        'severity': generate_severity_chart(engine.get_severity_distribution(), chart_dir),
    }
