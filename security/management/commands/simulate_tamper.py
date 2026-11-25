from django.core.management.base import BaseCommand
from parcels.models import Parcel
from security.models import AuditLog

class Command(BaseCommand):
    help = "Simulate DB-level silent tampering without updating the SHA-256 fingerprint. Demonstrates cryptographic tamper detection in the SOC dashboard."

    def add_arguments(self, parser):
        parser.add_argument('--parcel-id', type=str, help="Specific parcel ULPIN to tamper with (optional)")

    def handle(self, *args, **options):
        parcel_id = options.get('parcel_id')
        if parcel_id:
            parcel = Parcel.objects.filter(parcel_id=parcel_id).first()
        else:
            parcel = Parcel.objects.filter(status='Verified').first()

        if not parcel:
            self.stdout.write(self.style.ERROR("No suitable parcel found to tamper with."))
            return

        self.stdout.write(f"Targeting parcel: {parcel.parcel_id} (Khasra: {parcel.khasra_no})")
        self.stdout.write(f"Original Area: {parcel.area_hectares} ha | Fingerprint: {parcel.fingerprint}")

        # Silently update field in DB directly (bypassing model .save() fingerprint recalculation)
        old_area = parcel.area_hectares
        new_area = round(old_area + 2.50, 2)
        
        # Raw queryset update leaves stored fingerprint untouched!
        Parcel.objects.filter(id=parcel.id).update(area_hectares=new_area)

        self.stdout.write(self.style.WARNING(
            f"⚠️ SILENT TAMPER APPLIED: Area altered from {old_area} ha to {new_area} ha directly in the database."
        ))
        self.stdout.write(self.style.NOTICE(
            f"The stored SHA-256 fingerprint remains '{parcel.fingerprint[:16]}...', which no longer matches real-time recalculation."
        ))
        self.stdout.write(self.style.SUCCESS(
            "👉 Run 'Verify All Parcels' on the SOC Dashboard (/soc/) or run integrity report to watch the security alert trigger and parcel turn red!"
        ))
