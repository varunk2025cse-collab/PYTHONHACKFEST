from django.urls import path
from . import views

app_name = 'grievance_dashboard'

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('department/', views.department_analysis, name='department'),
    path('region/', views.region_analysis, name='region'),
    path('category/', views.category_analysis, name='category'),
    path('text-insights/', views.text_insights, name='text_insights'),
    path('recommendations/', views.recommendations, name='recommendations'),
    path('reports/', views.reports, name='reports'),
    path('about/', views.about, name='about'),
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    # API
    path('api/kpis/', views.api_kpis, name='api_kpis'),
    path('api/trend/', views.api_trend, name='api_trend'),
    path('api/filtered/', views.api_filtered, name='api_filtered'),
    path('api/search/', views.api_search, name='api_search'),
]
