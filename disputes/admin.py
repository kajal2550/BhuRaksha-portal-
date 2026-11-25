from django.contrib import admin
from .models import Dispute

@admin.register(Dispute)
class DisputeAdmin(admin.ModelAdmin):
    list_display = ('case_number', 'parcel', 'dispute_type', 'complainant_name', 'status', 'created_at')
    list_filter = ('status', 'dispute_type')
    search_fields = ('case_number', 'parcel__parcel_id', 'complainant_name')
