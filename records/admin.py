from django.contrib import admin
from .models import Owner, OwnershipRecord, CropRecord, Scheme, SchemeEligibility

@admin.register(Owner)
class OwnerAdmin(admin.ModelAdmin):
    list_display = ('name', 'masked_aadhaar', 'masked_phone', 'pm_kisan_id')
    search_fields = ('name', 'pm_kisan_id')

@admin.register(OwnershipRecord)
class OwnershipRecordAdmin(admin.ModelAdmin):
    list_display = ('parcel', 'owner', 'share_percentage', 'status', 'from_date')
    list_filter = ('status',)
    search_fields = ('parcel__parcel_id', 'owner__name')

@admin.register(CropRecord)
class CropRecordAdmin(admin.ModelAdmin):
    list_display = ('parcel', 'crop', 'season', 'sowing_date', 'estimated_yield_quintals')
    list_filter = ('season', 'crop')

@admin.register(Scheme)
class SchemeAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'subsidy_amount_per_ha')

@admin.register(SchemeEligibility)
class SchemeEligibilityAdmin(admin.ModelAdmin):
    list_display = ('parcel', 'scheme', 'is_eligible', 'checked_at')
