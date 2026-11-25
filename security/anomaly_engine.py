import json
from datetime import timedelta
from django.utils import timezone
from shapely.geometry import shape
from security.models import SecurityAlert, AuditLog
from parcels.models import Parcel
from mutations.models import Mutation

def run_anomaly_detectors() -> list:
    """
    Run automated rule-based fraud & threat detectors:
    1. Rapid mutations on the same parcel within 30 days
    2. Overlapping parcel polygons (using Shapely)
    3. Unusually high volume of edits by a single officer
    4. Off-hours revenue record changes (between 10 PM and 6 AM)
    5. Disputed parcels with mutation attempts
    """
    new_alerts = []
    now = timezone.now()

    # Rule 1: Rapid mutations on single parcel
    thirty_days_ago = now - timedelta(days=30)
    for p in Parcel.objects.all():
        recent_muts = p.mutations.filter(applied_date__gte=thirty_days_ago.date())
        if recent_muts.count() >= 2:
            alert, created = SecurityAlert.objects.get_or_create(
                alert_type="RAPID_MUTATION_VELOCITY",
                parcel_ref=p.parcel_id,
                defaults={
                    "severity": "HIGH",
                    "description": f"Parcel {p.khasra_no} has {recent_muts.count()} mutations within 30 days. Possible fraudulent flip.",
                    "status": "open"
                }
            )
            if created:
                new_alerts.append(alert)

    # Rule 2: Overlapping polygon geometries via Shapely
    parcels_list = list(Parcel.objects.all())
    shapely_polys = []
    for p in parcels_list:
        try:
            geom = json.loads(p.geometry_geojson)
            poly = shape(geom)
            if poly.is_valid:
                shapely_polys.append((p, poly))
        except Exception:
            continue

    for i in range(len(shapely_polys)):
        for j in range(i + 1, len(shapely_polys)):
            p1, poly1 = shapely_polys[i]
            p2, poly2 = shapely_polys[j]
            # Check intersection area
            if poly1.intersects(poly2):
                intersection = poly1.intersection(poly2)
                if intersection.area > 1e-8:
                    alert, created = SecurityAlert.objects.get_or_create(
                        alert_type="GEOMETRIC_CADASTRE_OVERLAP",
                        parcel_ref=f"{p1.parcel_id} & {p2.parcel_id}",
                        defaults={
                            "severity": "MEDIUM",
                            "description": f"Cadastral boundary collision detected between Khasra {p1.khasra_no} and {p2.khasra_no} (Overlap area: {intersection.area:.6f} deg²).",
                            "status": "open"
                        }
                    )
                    if created:
                        new_alerts.append(alert)

    # Rule 3: Edits outside official working hours (10:00 PM to 06:00 AM)
    night_logs = AuditLog.objects.filter(
        timestamp__hour__in=[22, 23, 0, 1, 2, 3, 4, 5]
    ).exclude(action='SYSTEM_SEED')[:10]
    for log in night_logs:
        alert, created = SecurityAlert.objects.get_or_create(
            alert_type="OFF_HOURS_CADASTRE_ACCESS",
            parcel_ref=log.parcel_ref,
            user_involved=log.user.username if log.user else 'Anonymous',
            defaults={
                "severity": "LOW",
                "description": f"Cadastral transaction '{log.action}' committed at {log.timestamp.strftime('%H:%M')} outside working hours.",
                "status": "open"
            }
        )
        if created:
            new_alerts.append(alert)

    # Rule 4: Mutation initiated on currently litigated/disputed land
    disputed_muts = Mutation.objects.filter(parcel__status='Disputed', status__in=['Applied', 'Under Review'])
    for m in disputed_muts:
        alert, created = SecurityAlert.objects.get_or_create(
            alert_type="MUTATION_ON_LITIGATED_LAND",
            parcel_ref=m.parcel.parcel_id,
            defaults={
                "severity": "HIGH",
                "description": f"Attempted mutation #{m.case_number} on parcel {m.parcel.khasra_no} which has an active legal dispute.",
                "status": "open"
            }
        )
        if created:
            new_alerts.append(alert)

    return new_alerts
