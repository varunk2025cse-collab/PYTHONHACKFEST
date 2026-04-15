import json
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.http import require_GET
from .analysis.engine import GrievanceEngine
from .services.chart_service import generate_all_charts
from .services.mongo_service import MongoService

_engine = None

def get_engine():
    global _engine
    if _engine is None:
        _engine = GrievanceEngine(str(settings.GRIEVANCE_CSV_PATH))
        _engine.load_data().clean_data()
    return _engine

def get_charts():
    return generate_all_charts(get_engine(), str(settings.CHART_DIR))

def home(request):
    engine = get_engine()
    kpis = engine.get_summary_kpis()
    insights = engine.generate_insights()
    return render(request, 'grievance_dashboard/home.html', {'kpis': kpis, 'alerts': insights['alerts'][:4], 'page': 'home', 'top_cats': insights['top_categories'][:3], 'top_depts': insights['top_complaint_departments'][:3]})

def dashboard(request):
    engine = get_engine()
    kpis = engine.get_summary_kpis()
    insights = engine.generate_insights()
    charts = get_charts()
    trend = engine.get_trend_data()
    status_dist = engine.get_status_distribution()
    severity_dist = engine.get_severity_distribution()
    mode_dist = engine.get_mode_distribution()
    yearly = engine.get_yearly_comparison()
    unique = engine.get_unique_values()
    context = {
        'kpis': kpis, 'insights': insights, 'charts': charts,
        'trend_json': json.dumps(trend), 'status_json': json.dumps(status_dist),
        'severity_json': json.dumps(severity_dist), 'mode_json': json.dumps(mode_dist),
        'yearly_json': json.dumps(yearly), 'unique': unique, 'page': 'dashboard',
    }
    return render(request, 'grievance_dashboard/dashboard.html', context)

def department_analysis(request):
    engine = get_engine()
    dept_df = engine.get_department_analysis()
    charts = get_charts()
    selected_dept = request.GET.get('dept', '')
    dept_trend = {}
    if selected_dept and selected_dept in dept_df['department'].values:
        dept_trend = engine.get_department_trend(selected_dept)
    context = {
        'departments': dept_df.to_dict('records'), 'charts': charts,
        'dept_trend_json': json.dumps(dept_trend), 'selected_dept': selected_dept,
        'dept_list': dept_df['department'].tolist(), 'page': 'department',
    }
    return render(request, 'grievance_dashboard/department.html', context)

def region_analysis(request):
    engine = get_engine()
    region_df = engine.get_region_analysis()
    charts = get_charts()
    context = {
        'regions': region_df.to_dict('records'), 'charts': charts,
        'region_json': json.dumps({'labels': region_df['region'].tolist(), 'total': region_df['total'].tolist(), 'risk_score': region_df['risk_score'].tolist(), 'unresolved_rate': region_df['unresolved_rate'].tolist()}),
        'page': 'region',
    }
    return render(request, 'grievance_dashboard/region.html', context)

def category_analysis(request):
    engine = get_engine()
    cat_df = engine.get_category_analysis()
    charts = get_charts()
    context = {
        'categories': cat_df.to_dict('records'), 'charts': charts,
        'cat_json': json.dumps({'labels': cat_df['category'].tolist(), 'total': cat_df['total'].tolist(), 'resolution_rate': cat_df['resolution_rate'].tolist(), 'avg_days': cat_df['avg_resolution_days'].tolist()}),
        'page': 'category',
    }
    return render(request, 'grievance_dashboard/category.html', context)

def text_insights(request):
    engine = get_engine()
    keywords = engine.get_keyword_frequencies(40)
    themes = engine.get_grievance_themes()
    context = {'keywords': keywords, 'themes': themes, 'keywords_json': json.dumps(keywords), 'page': 'text_insights'}
    return render(request, 'grievance_dashboard/text_insights.html', context)

def recommendations(request):
    engine = get_engine()
    insights = engine.generate_insights()
    kpis = engine.get_summary_kpis()
    context = {
        'recommendations': insights['recommendations'], 'alerts': insights['alerts'],
        'kpis': kpis, 'worst_depts': insights['worst_performing_departments'],
        'high_risk_regions': insights['high_risk_regions'], 'page': 'recommendations',
    }
    return render(request, 'grievance_dashboard/recommendations.html', context)

def reports(request):
    engine = get_engine()
    insights = engine.generate_insights()
    kpis = engine.get_summary_kpis()
    dept_df = engine.get_department_analysis()
    region_df = engine.get_region_analysis()
    cat_df = engine.get_category_analysis()
    charts = get_charts()
    context = {
        'kpis': kpis, 'insights': insights, 'charts': charts,
        'top_depts': dept_df.head(5).to_dict('records'),
        'top_regions': region_df.head(5).to_dict('records'),
        'top_cats': cat_df.head(5).to_dict('records'), 'page': 'reports',
    }
    return render(request, 'grievance_dashboard/reports.html', context)

def about(request):
    return render(request, 'grievance_dashboard/about.html', {'page': 'about'})

def admin_panel(request):
    engine = get_engine()
    kpis = engine.get_summary_kpis()
    unique = engine.get_unique_values()
    context = {
        'kpis': kpis, 'unique': unique, 'mongo_status': MongoService.is_connected(),
        'csv_path': str(settings.GRIEVANCE_CSV_PATH), 'page': 'admin',
    }
    return render(request, 'grievance_dashboard/admin_panel.html', context)

@require_GET
def api_kpis(request):
    return JsonResponse(get_engine().get_summary_kpis())

@require_GET
def api_trend(request):
    return JsonResponse(get_engine().get_trend_data())

@require_GET
def api_filtered(request):
    engine = get_engine()
    filtered = engine.get_filtered_data(
        request.GET.get('department', 'All'), request.GET.get('region', 'All'),
        request.GET.get('category', 'All'), request.GET.get('year', 'All'),
        request.GET.get('severity', 'All')
    )
    total = len(filtered)
    resolved = int(filtered['is_resolved'].sum())
    avg_days = float(filtered.loc[filtered['is_resolved'], 'resolution_days'].mean() or 0)
    return JsonResponse({'total': total, 'resolved': resolved, 'pending': total - resolved,
                         'avg_resolution_days': round(avg_days, 1),
                         'resolution_rate': round(resolved / total * 100, 1) if total else 0})

@require_GET
def api_search(request):
    query = request.GET.get('q', '').lower()
    if not query or len(query) < 2:
        return JsonResponse({'results': []})
    engine = get_engine()
    df = engine.df.copy()
    mask = (df['description'].str.lower().str.contains(query, na=False) |
            df['department'].str.lower().str.contains(query, na=False) |
            df['category'].str.lower().str.contains(query, na=False) |
            df['region'].str.lower().str.contains(query, na=False))
    results = df[mask].head(20)[['complaint_id', 'department', 'category', 'region', 'status', 'severity', 'complaint_date']].copy()
    results['complaint_date'] = results['complaint_date'].astype(str)
    return JsonResponse({'results': results.to_dict('records')})
