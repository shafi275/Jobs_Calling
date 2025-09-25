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
