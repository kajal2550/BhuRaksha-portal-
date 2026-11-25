from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from .models import Mutation, MutationStepComment, Document
from parcels.models import Parcel
from records.models import Owner, OwnershipRecord
from security.integrity_service import log_security_event

def mutations_list_view(request):
    """Multi-step mutation workflow module."""
    if request.method == 'POST':
        # New mutation submission
        parcel_id = request.POST.get('parcel_id')
        mutation_type = request.POST.get('mutation_type')
        applicant_name = request.POST.get('applicant_name')
        transferor_name = request.POST.get('transferor_name')
        remarks = request.POST.get('remarks')

        parcel = get_object_or_404(Parcel, id=parcel_id)
        case_no = f"MUT/PB/2024/{Mutation.objects.count() + 601}"

        mut = Mutation.objects.create(
            case_number=case_no,
            parcel=parcel,
            mutation_type=mutation_type,
            applicant_name=applicant_name,
            transferor_name=transferor_name,
            status='Applied',
            remarks=remarks
        )

        MutationStepComment.objects.create(
            mutation=mut,
            officer=request.user if request.user.is_authenticated else None,
            step_name="Application Filed",
            comment="Application entered into BhuRaksha mutation docket."
        )

        log_security_event(request.user, "APPLY_MUTATION", parcel.parcel_id, new_vals={"case": case_no, "applicant": applicant_name}, request=request)
        messages.success(request, f"Mutation Application #{case_no} successfully filed for Parcel Khasra {parcel.khasra_no}!")
        return redirect('mutations')

    mutations = Mutation.objects.select_related('parcel', 'parcel__village').order_by('-id')
    parcels = Parcel.objects.all()

    return render(request, 'mutations/mutations_list.html', {
        'mutations': mutations,
        'parcels': parcels,
        'applied_count': mutations.filter(status='Applied').count(),
        'review_count': mutations.filter(status='Under Review').count(),
        'completed_count': mutations.filter(status='Completed').count(),
    })


def mutation_detail_view(request, pk):
    mut = get_object_or_404(Mutation.objects.select_related('parcel', 'assigned_officer'), pk=pk)
    steps = mut.steps.select_related('officer').all()

    is_officer = request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role in ['revenue_officer', 'admin'])

    if request.method == 'POST' and is_officer:
        new_status = request.POST.get('status')
        comment_text = request.POST.get('comment', '').strip()

        old_status = mut.status
        mut.status = new_status

        if new_status == 'Approved':
            mut.approved_date = timezone.now().date()
        elif new_status == 'Completed':
            mut.completion_date = timezone.now().date()
            # AUTOMATICALLY UPDATE OWNERSHIP ON COMPLETION!
            # Retire transferor ownership & add applicant
            transferor_owner = Owner.objects.filter(name__icontains=mut.transferor_name).first()
            if transferor_owner:
                mut.parcel.ownership_records.filter(owner=transferor_owner).update(status='Transferred', to_date=timezone.now().date())
            
            # Create or get applicant owner
            app_owner, _ = Owner.objects.get_or_create(
                name=mut.applicant_name,
                defaults={"address": f"Village {mut.parcel.village.name}"}
            )
            app_owner.set_aadhaar("XXXX-XXXX-9912")
            app_owner.set_phone("+91 98144 00000")
            app_owner.save()

            OwnershipRecord.objects.create(
                parcel=mut.parcel,
                owner=app_owner,
                share_percentage=100.0,
                status='Active'
            )
            mut.parcel.status = 'Verified'
            mut.parcel.save()

        mut.save()

        # Step record
        MutationStepComment.objects.create(
            mutation=mut,
            officer=request.user,
            step_name=f"Status changed to {new_status}",
            comment=comment_text or "Verified in Revenue records by Revenue Officer."
        )

        log_security_event(request.user, f"MUTATION_{new_status.upper()}", mut.parcel.parcel_id, old_vals={"status": old_status}, new_vals={"status": new_status}, request=request)
        messages.success(request, f"Mutation #{mut.case_number} updated to '{new_status}'.")
        return redirect('mutation_detail', pk=mut.id)

    return render(request, 'mutations/mutation_detail.html', {'mutation': mut, 'steps': steps, 'is_officer': is_officer})
