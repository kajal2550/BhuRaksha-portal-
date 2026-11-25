from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from .models import Dispute
from parcels.models import Parcel
from security.integrity_service import log_security_event

def disputes_list_view(request):
    """Dispute management view."""
    if request.method == 'POST':
        parcel_id = request.POST.get('parcel_id')
        dispute_type = request.POST.get('dispute_type')
        complainant_name = request.POST.get('complainant_name')
        contact = request.POST.get('complainant_contact')
        description = request.POST.get('description')
        pin_lat = request.POST.get('pin_lat')
        pin_lng = request.POST.get('pin_lng')

        parcel = get_object_or_404(Parcel, id=parcel_id)
        case_no = f"DSP/PB/2024/{Dispute.objects.count() + 201}"

        dispute = Dispute.objects.create(
            case_number=case_no,
            parcel=parcel,
            dispute_type=dispute_type,
            complainant_name=complainant_name,
            complainant_contact=contact,
            complainant_user=request.user if request.user.is_authenticated else None,
            description=description,
            pin_lat=float(pin_lat) if pin_lat else parcel.centroid_lat,
            pin_lng=float(pin_lng) if pin_lng else parcel.centroid_lng,
            status='Open'
        )

        log_security_event(request.user, "RAISE_LEGAL_DISPUTE", parcel.parcel_id, new_vals={"case": case_no, "type": dispute_type}, request=request)
        messages.success(request, f"Legal Dispute #{case_no} registered on Khasra {parcel.khasra_no}. Parcel marked as Disputed.")
        return redirect('disputes_list')

    disputes = Dispute.objects.select_related('parcel', 'parcel__village').order_by('-id')
    parcels = Parcel.objects.all()

    return render(request, 'disputes/disputes_list.html', {
        'disputes': disputes,
        'parcels': parcels,
        'open_count': disputes.filter(status='Open').count(),
        'review_count': disputes.filter(status='In Review').count(),
        'resolved_count': disputes.filter(status='Resolved').count()
    })


def dispute_detail_view(request, pk):
    dispute = get_object_or_404(Dispute.objects.select_related('parcel', 'assigned_officer'), pk=pk)
    is_officer = request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role in ['revenue_officer', 'admin'])

    if request.method == 'POST' and is_officer:
        new_status = request.POST.get('status')
        notes = request.POST.get('resolution_notes')
        
        dispute.status = new_status
        dispute.resolution_notes = notes
        if new_status in ['Resolved', 'Closed']:
            dispute.resolved_at = timezone.now()
            # If no more open disputes on parcel, restore Verified status
            other_open = Dispute.objects.filter(parcel=dispute.parcel, status__in=['Open', 'In Review']).exclude(id=dispute.id).exists()
            if not other_open:
                dispute.parcel.status = 'Verified'
                dispute.parcel.save()

        dispute.save()
        log_security_event(request.user, f"DISPUTE_{new_status.upper()}", dispute.parcel.parcel_id, new_vals={"case": dispute.case_number}, request=request)
        messages.success(request, f"Dispute #{dispute.case_number} status updated to {new_status}.")
        return redirect('dispute_detail', pk=dispute.id)

    return render(request, 'disputes/dispute_detail.html', {'dispute': dispute, 'is_officer': is_officer})
