from django.shortcuts import render
from django.db.models import Sum, Count
from parcels.models import Parcel, Village
from records.models import Owner
from mutations.models import Mutation
from disputes.models import Dispute
from security.models import SecurityAlert

def home_view(request):
    """Page 1: Landing / Home Page."""
    total_parcels = Parcel.objects.count()
    total_area_ha = Parcel.objects.aggregate(total=Sum('area_hectares'))['total'] or 0.0
    total_mutations = Mutation.objects.count()
    total_disputes = Dispute.objects.filter(status__in=['Open', 'In Review']).count()
    verified_count = Parcel.objects.filter(status='Verified').count()
    verified_pct = round((verified_count / total_parcels * 100), 1) if total_parcels else 100
    pm_kisan_count = Owner.objects.exclude(pm_kisan_id__isnull=True).exclude(pm_kisan_id='').count()
    active_alerts = SecurityAlert.objects.filter(status='open').count()

    context = {
        'total_parcels': total_parcels,
        'total_area_ha': round(total_area_ha, 2),
        'total_mutations': total_mutations,
        'total_disputes': total_disputes,
        'verified_percentage': verified_pct,
        'pm_kisan_count': pm_kisan_count,
        'active_alerts_count': active_alerts,
    }
    return render(request, 'core/home.html', context)

def about_view(request):
    return render(request, 'core/about.html')

def architecture_view(request):
    return render(request, 'core/architecture.html')

def threat_model_view(request):
    return render(request, 'core/threat_model.html')

def security_policy_view(request):
    return render(request, 'core/security_policy.html')

def help_faq_view(request):
    return render(request, 'core/help_faq.html')

def api_docs_view(request):
    """Page 15: Open API & Developer Hub."""
    return render(request, 'core/api_docs.html')

def error_403(request, exception=None):
    return render(request, 'core/403.html', status=403)

def error_404(request, exception=None):
    return render(request, 'core/404.html', status=404)

def error_500(request):
    return render(request, 'core/500.html', status=500)
