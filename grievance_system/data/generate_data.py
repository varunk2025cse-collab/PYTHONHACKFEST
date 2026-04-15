import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

random.seed(42)
np.random.seed(42)

departments = [
    "Water Supply", "Roads & Infrastructure", "Electricity Board",
    "Municipal Sanitation", "Health Services", "Public Transport",
    "Revenue Department", "Education Department", "Housing Authority",
    "Police Department", "Fire Services", "Environment Department"
]

regions = [
    "North District", "South District", "East District", "West District",
    "Central Zone", "Industrial Area", "Suburban Area", "Old City",
    "New Township", "Riverside Block", "Hill Station", "Coastal Ward"
]

categories = [
    "Water Shortage", "Road Damage", "Power Outage", "Garbage Collection",
    "Street Light Failure", "Drainage Issue", "Hospital Service",
    "Bus Route Issue", "Property Tax", "School Facilities",
    "Noise Pollution", "Air Pollution", "Encroachment", "Corruption",
    "Poor Service", "Delayed Response", "Documentation Issue",
    "Water Quality", "Road Construction Delay", "Sewage Overflow"
]

statuses = ["Resolved", "Pending", "In Progress", "Closed", "Reopened"]
status_weights = [0.45, 0.25, 0.15, 0.10, 0.05]

severities = ["Low", "Medium", "High", "Critical"]
sev_weights = [0.20, 0.40, 0.28, 0.12]

complaint_templates = {
    "Water Shortage": [
        "No water supply for past {} days in our area",
        "Water pipeline broken causing shortage since {}",
        "Irregular water supply affecting {} households",
        "Contaminated water supply reported in {} locality"
    ],
    "Road Damage": [
        "Pothole on main road causing accidents near {}",
        "Road completely damaged after rains near {}",
        "Street not repaired since {} months in {} area",
        "Broken road surface causing vehicle damage in {}"
    ],
    "Power Outage": [
        "No electricity for {} hours continuously",
        "Frequent power cuts {} times daily in our ward",
        "Transformer damaged causing outage in {} area",
        "Power fluctuation damaging home appliances in {}"
    ],
    "Garbage Collection": [
        "Garbage not collected for {} days",
        "Overflowing dustbin near {} area not cleaned",
        "Garbage dumped on road since {} week near {}",
        "No sanitation vehicle visiting our locality since {}"
    ],
    "Drainage Issue": [
        "Drain blocked causing flooding in {} area",
        "Sewage overflow on main road near {}",
        "Drainage pipe broken for {} weeks",
        "Stagnant water breeding mosquitoes near {}"
    ],
}

default_templates = [
    "Serious issue regarding {} in our locality",
    "Urgent complaint about {} affecting citizens",
    "No action taken on {} complaint since {} days",
    "Repeated complaint about {} in {} area still unresolved"
]

def generate_description(category, region):
    templates = complaint_templates.get(category, default_templates)
    template = random.choice(templates)
    placeholders = template.count("{}")
    values = [random.choice([str(random.randint(2, 30)), region, "our", "this"]) for _ in range(placeholders)]
    try:
        return template.format(*values)
    except:
        return f"Complaint regarding {category} in {region} area requires immediate attention."

start_date = datetime(2022, 1, 1)
end_date = datetime(2024, 12, 31)

n = 2000
records = []

for i in range(n):
    dept = random.choice(departments)
    region = random.choice(regions)
    category = random.choice(categories)
    status = random.choices(statuses, weights=status_weights)[0]
    severity = random.choices(severities, weights=sev_weights)[0]

    # Bias certain departments to have more complaints
    if dept in ["Water Supply", "Roads & Infrastructure", "Municipal Sanitation"]:
        region = random.choices(regions, weights=[3,1,1,1,2,1,2,3,1,1,1,1])[0]

    complaint_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))

    if status in ["Resolved", "Closed"]:
        if severity == "Critical":
            res_days = random.randint(1, 10)
        elif severity == "High":
            res_days = random.randint(3, 25)
        elif severity == "Medium":
            res_days = random.randint(5, 45)
        else:
            res_days = random.randint(10, 90)
        resolution_date = complaint_date + timedelta(days=res_days)
    else:
        resolution_date = None
        res_days = None

    citizen_id = f"CIT{random.randint(10000, 99999)}"
    complaint_id = f"GRV{str(i+1).zfill(5)}"

    records.append({
        "complaint_id": complaint_id,
        "citizen_id": citizen_id,
        "department": dept,
        "region": region,
        "category": category,
        "severity": severity,
        "status": status,
        "complaint_date": complaint_date.strftime("%Y-%m-%d"),
        "resolution_date": resolution_date.strftime("%Y-%m-%d") if resolution_date else "",
        "resolution_days": res_days,
        "description": generate_description(category, region),
        "citizen_rating": random.randint(1, 5) if status in ["Resolved", "Closed"] else "",
        "mode_of_complaint": random.choice(["Online Portal", "Mobile App", "Walk-in", "Phone", "Email"]),
        "assigned_officer": f"Officer_{random.randint(100, 500)}"
    })

df = pd.DataFrame(records)
df.to_csv("grievance_data.csv", index=False)
print(f"Generated {len(df)} records")
print(df.head())
print(df.dtypes)
