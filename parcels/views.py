import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Count, Q
from django.contrib import messages
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from parcels.models import Parcel, Village
from records.models import Owner, OwnershipRecord, CropRecord, Scheme, SchemeEligibility
from mutations.models import Mutation, MutationStepComment, Document
from disputes.models import Dispute
from security.models import AuditLog, SecurityAlert
from security.integrity_service import log_security_event, run_full_integrity_check
from .serializers import ParcelDetailSerializer

# 1. Main GIS Map View (Centerpiece)
def map_view(request):
    parcels = Parcel.objects.select_related('village').all()
    villages = Village.objects.all()
    crops = CropRecord.objects.values_list('crop', flat=True).distinct()
    
    # Check if current user is farmer and has linked parcels
    user_parcels_ids = []
    if request.user.is_authenticated and hasattr(request.user, 'profile') and request.user.profile.role == 'farmer':
        # Find owners matching username/name or phone
        user_parcels_ids = list(OwnershipRecord.objects.filter(
            Q(owner__name__icontains=request.user.first_name) | Q(owner__encrypted_phone__icontains=request.user.username)
        ).values_list('parcel_id', flat=True))

    context = {
        'parcels': parcels,
        'villages': villages,
        'crops': crops,
        'total_parcels': parcels.count(),
        'user_parcels_json': json.dumps(user_parcels_ids) if 'json' in globals() else "[]"
    }
    return render(request, 'parcels/map.html', context)


# 2. Parcel Detail Page (Full Page Version of Side Panel)
def parcel_detail_view(request, pk):
    parcel = get_object_or_404(Parcel.objects.select_related('village').prefetch_related(
        'ownership_records__owner', 'crop_records', 'mutations', 'disputes', 'documents'
    ), pk=pk)

    # Role-based masking: only Revenue Officer, Admin, or the owner themselves sees plain Aadhaar
    can_view_pii = False
    if request.user.is_authenticated:
        if request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role in ['revenue_officer', 'admin']):
            can_view_pii = True

    ownerships = parcel.ownership_records.all()
    crops = parcel.crop_records.all()
    mutations = parcel.mutations.all()
    disputes = parcel.disputes.all()
    documents = parcel.documents.all()
    schemes = parcel.scheme_eligibilities.select_related('scheme').all()
    audit_logs = AuditLog.objects.filter(parcel_ref=parcel.parcel_id).order_by('-id')[:20]

    integrity_ok = parcel.verify_integrity()

    context = {
        'parcel': parcel,
        'can_view_pii': can_view_pii,
        'ownerships': ownerships,
        'crops': crops,
        'mutations': mutations,
        'disputes': disputes,
        'documents': documents,
        'schemes': schemes,
        'audit_logs': audit_logs,
        'integrity_ok': integrity_ok
    }
    return render(request, 'parcels/parcel_detail.html', context)


# 3. Public Parcel Verification Page (Scan QR or Enter Parcel ID)
def verify_public_view(request):
    query = request.GET.get('parcel_id', '').strip()
    parcel = None
    integrity_status = None

    if query:
        parcel = Parcel.objects.filter(Q(parcel_id__iexact=query) | Q(khasra_no__iexact=query)).first()
        if parcel:
            integrity_status = {
                "valid": parcel.verify_integrity(),
                "fingerprint": parcel.fingerprint,
                "recalc": parcel.calculate_fingerprint(),
                "status": parcel.status
            }
            # Log public query
            log_security_event(request.user, "PUBLIC_VERIFY_QUERY", parcel.parcel_id, request=request)
        else:
            messages.error(request, f"No cadastral record matching '{query}' found.")

    return render(request, 'parcels/verify_public.html', {'parcel': parcel, 'integrity': integrity_status, 'query': query})


# 4. Cadastral Register (Searchable table)
def register_view(request):
    q = request.GET.get('q', '').strip()
    village_id = request.GET.get('village', '').strip()
    land_use = request.GET.get('land_use', '').strip()
    status = request.GET.get('status', '').strip()

    qs = Parcel.objects.select_related('village').prefetch_related('ownership_records__owner', 'crop_records').all()

    if q:
        qs = qs.filter(
            Q(khasra_no__icontains=q) |
            Q(parcel_id__icontains=q) |
            Q(ownership_records__owner__name__icontains=q)
        ).distinct()

    if village_id:
        qs = qs.filter(village_id=village_id)
    if land_use:
        qs = qs.filter(land_use_type=land_use)
    if status:
        qs = qs.filter(status=status)

    villages = Village.objects.all()

    return render(request, 'parcels/register.html', {
        'parcels': qs,
        'villages': villages,
        'q': q,
        'selected_village': village_id,
        'selected_land_use': land_use,
        'selected_status': status,
        'count': qs.count()
    })


# 5. Export QGIS GeoJSON
def export_qgis_geojson(request):
    try:
        req_obj = getattr(request, '_request', request)
        resp = parcel_geojson_list_api(req_obj)
        data = json.dumps(resp.data)
    except Exception:
        parcels = Parcel.objects.all()
        features = [p.to_geojson_feature() for p in parcels]
        geojson_data = {
            "type": "FeatureCollection",
            "features": features
        }
        data = json.dumps(geojson_data)
    response = HttpResponse(data, content_type='application/geo+json')
    response['Content-Disposition'] = 'attachment; filename="bhuraksha_cadastre_qgis.geojson"'
    return response


# 6. REST API: GeoJSON FeatureCollection
@api_view(['GET'])
@permission_classes([AllowAny])
def parcel_geojson_list_api(request):
    q = request.GET.get('q', '').strip()
    land_use = request.GET.get('land_use', '').strip()
    crop = request.GET.get('crop', '').strip()
    status = request.GET.get('status', '').strip()
    village = request.GET.get('village', '').strip()

    qs = Parcel.objects.select_related('village').prefetch_related('ownership_records__owner', 'crop_records', 'mutations').all()

    if q:
        qs = qs.filter(
            Q(khasra_no__icontains=q) |
            Q(parcel_id__icontains=q) |
            Q(ownership_records__owner__name__icontains=q)
        ).distinct()

    if land_use:
        qs = qs.filter(land_use_type=land_use)
    if crop:
        qs = qs.filter(crop_records__crop__icontains=crop).distinct()
    if status:
        qs = qs.filter(status=status)
    if village:
        qs = qs.filter(village__name__icontains=village)

    features = []
    for p in qs:
        try:
            geom = json.loads(p.geometry_geojson)
        except Exception:
            geom = None

        primary_owner = p.ownership_records.filter(status='Active').first()
        owner_name = primary_owner.owner.name if primary_owner else "Gram Panchayat"
        masked_id = primary_owner.owner.masked_aadhaar if primary_owner else "N/A"
        pm_kisan = bool(primary_owner and primary_owner.owner.pm_kisan_id)

        latest_crop = p.crop_records.first()
        crop_name = f"{latest_crop.crop} ({latest_crop.season})" if latest_crop else "Fallow"

        features.append({
            "type": "Feature",
            "id": p.id,
            "geometry": geom,
            "properties": {
                "id": p.id,
                "parcel_id": p.parcel_id,
                "khasra_no": p.khasra_no,
                "village": p.village.name,
                "owner_name": owner_name,
                "masked_aadhaar": masked_id,
                "pm_kisan": pm_kisan,
                "area_ha": p.area_hectares,
                "area_acres": p.area_acres,
                "land_use_type": p.land_use_type,
                "soil_type": p.soil_type,
                "irrigation_source": p.irrigation_source,
                "status": p.status,
                "crop": crop_name,
                "fingerprint": p.fingerprint[:12] + "...",
                "centroid": [p.centroid_lat, p.centroid_lng]
            }
        })

    return Response({
        "type": "FeatureCollection",
        "features": features
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def parcel_detail_api(request, parcel_id):
    try:
        parcel = Parcel.objects.select_related('village').prefetch_related(
            'ownership_records__owner', 'crop_records', 'mutations', 'documents'
        ).get(parcel_id=parcel_id)
    except Parcel.DoesNotExist:
        parcel = get_object_or_404(Parcel, pk=parcel_id)
    return Response(ParcelDetailSerializer(parcel).data)
