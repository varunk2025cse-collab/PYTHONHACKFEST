import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'grievance_system.settings')
django.setup()

from django.test import Client
from django.urls import reverse

client = Client()

urls = [
    'grievance_dashboard:home',
    'grievance_dashboard:dashboard',
    'grievance_dashboard:department',
    'grievance_dashboard:region',
    'grievance_dashboard:category',
    'grievance_dashboard:text_insights',
    'grievance_dashboard:recommendations',
    'grievance_dashboard:reports',
    'grievance_dashboard:about',
    'grievance_dashboard:admin_panel',
]

for url_name in urls:
    try:
        url = reverse(url_name)
        response = client.get(url)
        if response.status_code != 200:
            print(f"[{url_name}] returned status {response.status_code}")
        else:
            print(f"[{url_name}] OK")
    except Exception as e:
        print(f"[{url_name}] ERROR: {type(e).__name__} - {e}")
