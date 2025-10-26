from django.contrib import admin
from .models import CandidateProfile, CompanyProfile, JobPosting, JobApplication, CandidateResume


@admin.register(CandidateProfile)
class CandidateProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'user', 'agree_terms')
    search_fields = ('full_name', 'user__username', 'user__email')
    list_filter = ('agree_terms',)


@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'user', 'industry', 'company_size', 'contact_person', 'agree_terms')
    search_fields = ('company_name', 'user__username', 'user__email', 'industry')
    list_filter = ('industry', 'company_size', 'agree_terms')


@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'job_type', 'location', 'is_active', 'posted_date', 'application_deadline')
    list_filter = ('job_type', 'is_active', 'posted_date', 'location')
    search_fields = ('title', 'company__company_name', 'requirements', 'description')
    date_hierarchy = 'posted_date'
    ordering = ('-posted_date',)
    list_per_page = 20


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('job', 'candidate', 'status', 'application_date')
    list_filter = ('status', 'application_date')
    search_fields = ('job__title', 'candidate__full_name')
    date_hierarchy = 'application_date'
    ordering = ('-application_date',)
    list_per_page = 20


@admin.register(CandidateResume)
class CandidateResumeAdmin(admin.ModelAdmin):
    list_display = ('original_filename', 'candidate', 'file_size', 'content_type', 'uploaded_at')
    search_fields = ('original_filename', 'candidate__full_name', 'candidate__user__username')
    list_filter = ('uploaded_at',)
    readonly_fields = ('file_size', 'content_type', 'original_filename', 'uploaded_at')
    date_hierarchy = 'uploaded_at'
    ordering = ('-uploaded_at',)
    list_per_page = 20
