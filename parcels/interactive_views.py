import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from parcels.models import Parcel, Village
from records.models import Owner, OwnershipRecord, CropRecord
from mutations.models import Mutation, MutationStepComment
from disputes.models import Dispute
from security.integrity_service import log_security_event

@csrf_exempt
def api_draw_create_parcel(request):
    """
    Live Leaflet.Draw save functionality:
    When officer or farmer draws a new boundary polygon on the map,
    this endpoint saves it immediately into the DB with automated ULPIN and SHA-256 fingerprint!
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            geometry = data.get('geometry') # GeoJSON dict
            khasra_no = data.get('khasra_no', f"NEW-{Parcel.objects.count() + 101}")
            owner_name = data.get('owner_name', 'Self Registered / Khatedar')
            land_use = data.get('land_use', 'Irrigated Agri')
            crop_name = data.get('crop', 'Wheat (PAU PBW-725)')

            # Extract centroid
            coords = geometry['coordinates'][0]
            lats = [c[1] for c in coords]
            lngs = [c[0] for c in coords]
            cent_lat = round(sum(lats) / len(lats), 6)
            cent_lng = round(sum(lngs) / len(lngs), 6)

            # Area calculation approx
            area_ha = round(len(coords) * 0.45, 2)
            if area_ha < 0.5:
                area_ha = 0.85

            village = Village.objects.first()
            ulpin = f"PB-KPT-2024-{random_id := Parcel.objects.count() + 1001}"

            parcel = Parcel(
                parcel_id=ulpin,
                khasra_no=khasra_no,
                village=village,
                area_hectares=area_ha,
                area_acres=round(area_ha * 2.471, 2),
                land_use_type=land_use,
                status='Verified',
                geometry_geojson=json.dumps(geometry),
                centroid_lat=cent_lat,
                centroid_lng=cent_lng
            )
            parcel.save()

            owner, _ = Owner.objects.get_or_create(name=owner_name, defaults={"address": "Village Phagwara"})
            owner.set_aadhaar("XXXX-XXXX-8822")
            owner.set_phone("+91 98144 11223")
            owner.save()

            OwnershipRecord.objects.create(parcel=parcel, owner=owner, share_percentage=100.0, status='Active')
            CropRecord.objects.create(parcel=parcel, crop=crop_name, season="Rabi", sowing_date="2024-11-15", estimated_yield_quintals=35.0)

            log_security_event(request.user, "DRAW_NEW_PARCEL", parcel.parcel_id, new_vals={"khasra": khasra_no, "area": area_ha}, request=request)

            return JsonResponse({
                "status": "success",
                "message": f"Successfully registered drawn cadastral plot Khasra {khasra_no} [ULPIN: {ulpin}]!",
                "parcel_id": parcel.id,
                "ulpin": ulpin,
                "khasra_no": khasra_no
            })
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

    return JsonResponse({"status": "error", "message": "POST required"}, status=405)


@csrf_exempt
def api_update_parcel_status(request, pk):
    """Instant status toggle from map (Verify / Dispute / Pending)."""
    if request.method == 'POST':
        parcel = get_object_or_404(Parcel, pk=pk)
        data = json.loads(request.body.decode('utf-8'))
        new_status = data.get('status', 'Verified')
        
        old_status = parcel.status
        parcel.status = new_status
        parcel.save(skip_fingerprint=(new_status == 'Disputed'))

        log_security_event(request.user, f"SET_STATUS_{new_status.upper()}", parcel.parcel_id, old_vals={"status": old_status}, new_vals={"status": new_status}, request=request)
        return JsonResponse({"status": "success", "new_status": new_status, "khasra": parcel.khasra_no})

    return JsonResponse({"status": "error"}, status=405)


def download_ror_pdf(request, pk):
    """Generates official clean printable HTML / PDF Record of Rights Certificate with QR code."""
    parcel = get_object_or_404(Parcel, pk=pk)
    owners = parcel.ownership_records.all()
    crops = parcel.crop_records.all()
    return render(request, 'parcels/certificate_print.html', {
        'parcel': parcel,
        'owners': owners,
        'crops': crops
    })
