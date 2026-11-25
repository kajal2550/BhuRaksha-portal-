from django.contrib import admin
from .models import Mutation, MutationStepComment, Document

@admin.register(Mutation)
class MutationAdmin(admin.ModelAdmin):
    list_display = ('case_number', 'parcel', 'mutation_type', 'applicant_name', 'status', 'applied_date')
    list_filter = ('status', 'mutation_type')
    search_fields = ('case_number', 'applicant_name', 'parcel__parcel_id')

@admin.register(MutationStepComment)
class MutationStepCommentAdmin(admin.ModelAdmin):
    list_display = ('mutation', 'step_name', 'officer', 'timestamp')

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'parcel', 'doc_type', 'uploaded_at')
