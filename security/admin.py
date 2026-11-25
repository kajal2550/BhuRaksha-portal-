from django.contrib import admin
from .models import AuditLog, SecurityAlert, IntegrityReport, Notification, APIToken

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'action', 'parcel_ref', 'user', 'user_role', 'timestamp')
    readonly_fields = [f.name for f in AuditLog._meta.fields]
    search_fields = ('parcel_ref', 'action', 'current_hash')
    list_filter = ('action', 'user_role')

    def has_add_permission(self, request):
        return False
    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(SecurityAlert)
class SecurityAlertAdmin(admin.ModelAdmin):
    list_display = ('alert_type', 'severity', 'parcel_ref', 'status', 'created_at')
    list_filter = ('severity', 'status')

@admin.register(IntegrityReport)
class IntegrityReportAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'run_by', 'total_parcels_checked', 'passed_count', 'failed_count', 'hash_chain_valid')

@admin.register(APIToken)
class APITokenAdmin(admin.ModelAdmin):
    list_display = ('client_name', 'department_role', 'is_active', 'rate_limit_per_minute')
