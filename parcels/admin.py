from django.contrib import admin
from .models import Village, Parcel

@admin.register(Village)
class VillageAdmin(admin.ModelAdmin):
    list_display = ('name', 'village_code', 'tehsil', 'district', 'state')
    search_fields = ('name', 'village_code', 'tehsil')

@admin.register(Parcel)
class ParcelAdmin(admin.ModelAdmin):
    list_display = ('khasra_no', 'parcel_id', 'village', 'land_use_type', 'area_hectares', 'status', 'fingerprint')
    search_fields = ('khasra_no', 'parcel_id', 'village__name')
    list_filter = ('land_use_type', 'status', 'village')
    readonly_fields = ('fingerprint',)
