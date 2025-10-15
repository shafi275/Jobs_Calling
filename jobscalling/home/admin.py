from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import CandidateProfile, CompanyProfile

# Register CandidateProfile
@admin.register(CandidateProfile)
class CandidateProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'user', 'agree_terms')
    search_fields = ('full_name', 'user__username', 'user__email')

# Register CompanyProfile
@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'user', 'industry', 'company_size', 'contact_person', 'agree_terms')
    search_fields = ('company_name', 'user__username', 'user__email', 'industry')

from .models import CandidateResume


@admin.register(CandidateResume)
class CandidateResumeAdmin(admin.ModelAdmin):
    list_display = ('original_filename', 'candidate', 'file_size', 'content_type', 'uploaded_at')
    search_fields = ('original_filename', 'candidate__full_name', 'candidate__user__username')
    list_filter = ('uploaded_at',)
    readonly_fields = ('file_size', 'content_type', 'original_filename', 'uploaded_at')
