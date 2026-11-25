from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Sum, Count, Q
from django.contrib import messages
from .models import Owner, OwnershipRecord, CropRecord, Scheme, SchemeEligibility
from parcels.models import Parcel
from security.integrity_service import log_security_event

def owners_list_view(request):
    """Ownership and Records Management (Revenue Officer / Admin)."""
    q = request.GET.get('q', '').strip()
    owners = Owner.objects.prefetch_related('land_holdings__parcel').all()
    if q:
        owners = owners.filter(Q(name__icontains=q) | Q(pm_kisan_id__icontains=q))

    can_view_pii = request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role in ['revenue_officer', 'admin'])

    return render(request, 'records/owners.html', {'owners': owners, 'q': q, 'can_view_pii': can_view_pii})


def create_ownership_record_view(request):
    """Allows Revenue Officer to link an owner to a parcel with 100% share validation."""
    if request.method == 'POST':
        parcel_id = request.POST.get('parcel_id')
        owner_id = request.POST.get('owner_id')
        share_pct = float(request.POST.get('share_percentage', 100.0))

        parcel = get_object_or_404(Parcel, id=parcel_id)
        owner = get_object_or_404(Owner, id=owner_id)

        # Validate that total active shares do not exceed 100%
        current_active_shares = parcel.ownership_records.filter(status='Active').aggregate(total=Sum('share_percentage'))['total'] or 0.0
        if current_active_shares + share_pct > 100.001:
            messages.error(request, f"Validation Error: Total ownership shares would equal {current_active_shares + share_pct}%, which exceeds 100%.")
            return redirect('owners_list')

        rec = OwnershipRecord.objects.create(
            parcel=parcel,
            owner=owner,
            share_percentage=share_pct,
            status='Active'
        )
        log_security_event(request.user, "CREATE_OWNERSHIP_RECORD", parcel.parcel_id, new_vals={"owner": owner.name, "share": share_pct}, request=request)
        messages.success(request, f"Ownership of {share_pct}% registered for {owner.name} on Khasra {parcel.khasra_no}.")

    return redirect('owners_list')


def crops_list_view(request):
    """Crop and Land-Use Management (Agri Officer)."""
    crops = CropRecord.objects.select_related('parcel', 'parcel__village').all()
    parcels = Parcel.objects.all()
    schemes = Scheme.objects.all()

    if request.method == 'POST':
        parcel_id = request.POST.get('parcel_id')
        crop_name = request.POST.get('crop')
        season = request.POST.get('season')
        variety = request.POST.get('variety')
        sowing_date = request.POST.get('sowing_date')
        yield_val = float(request.POST.get('estimated_yield_quintals', 20.0))

        parcel = get_object_or_404(Parcel, id=parcel_id)
        CropRecord.objects.create(
            parcel=parcel,
            crop=crop_name,
            season=season,
            variety=variety,
            sowing_date=sowing_date,
            estimated_yield_quintals=yield_val,
            irrigation_used=parcel.irrigation_source
        )
        log_security_event(request.user, "LOG_CROP_CULTIVATION", parcel.parcel_id, new_vals={"crop": crop_name, "season": season}, request=request)
        messages.success(request, f"Crop entry logged: {crop_name} ({season}) on Khasra {parcel.khasra_no}.")
        return redirect('agriculture_hub')

    return render(request, 'records/crops.html', {'crops': crops, 'parcels': parcels, 'schemes': schemes})


def schemes_view(request):
    schemes = Scheme.objects.all()
    eligibilities = SchemeEligibility.objects.select_related('parcel', 'scheme').all()
    return render(request, 'records/schemes.html', {'schemes': schemes, 'eligibilities': eligibilities})
