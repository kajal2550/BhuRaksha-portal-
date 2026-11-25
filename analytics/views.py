import json
from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Sum, Count
from parcels.models import Parcel, Village
from records.models import CropRecord
from mutations.models import Mutation
from disputes.models import Dispute

def analytics_view(request):
    """Page 14: Analytics & Decision Support System (DSS) with Chart.js."""
    parcels = Parcel.objects.all()
    crops = CropRecord.objects.all()

    crop_chart_data = list(CropRecord.objects.values('crop').annotate(
        total_yield=Sum('estimated_yield_quintals'),
        count=Count('id')
    ).order_by('-total_yield'))

    landuse_chart_data = list(Parcel.objects.values('land_use_type').annotate(
        total_area=Sum('area_hectares'),
        count=Count('id')
    ))

    mutation_by_type = list(Mutation.objects.values('mutation_type').annotate(
        count=Count('id')
    ))

    dispute_by_status = list(Dispute.objects.values('status').annotate(
        count=Count('id')
    ))

    total_ha = parcels.aggregate(total=Sum('area_hectares'))['total'] or 0.0
    total_yield = crops.aggregate(total=Sum('estimated_yield_quintals'))['total'] or 0.0

    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="bhuraksha_analytics_summary.csv"'
        response.write("CATEGORY,METRIC,VALUE\n")
        response.write(f"Cadastre,Total Hectares,{total_ha:.2f}\n")
        response.write(f"Cadastre,Total Plots,{parcels.count()}\n")
        response.write(f"Agriculture,Estimated Harvest Yield (Qt),{total_yield:.2f}\n")
        response.write(f"Governance,Total Mutations,{Mutation.objects.count()}\n")
        response.write(f"Governance,Active Disputes,{Dispute.objects.count()}\n")
        return response

    context = {
        'total_ha': round(total_ha, 2),
        'total_yield': round(total_yield, 1),
        'total_parcels': parcels.count(),
        'total_mutations': Mutation.objects.count(),
        'total_disputes': Dispute.objects.count(),
        'crop_chart_data': json.dumps(crop_chart_data),
        'landuse_chart_data': json.dumps(landuse_chart_data),
        'mutation_chart_data': json.dumps(mutation_by_type),
        'dispute_chart_data': json.dumps(dispute_by_status),
    }
    return render(request, 'analytics/analytics.html', context)
