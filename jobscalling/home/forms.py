from django import forms
from .models import JobPosting

class JobPostingForm(forms.ModelForm):
    """
    A ModelForm for creating and updating JobPosting objects.
    """
    # Explicitly define fields for display order and control
    class Meta:
        model = JobPosting
        fields = [
            'title', 
            'description', 
            'location', 
            'job_type', 
            'min_salary', 
            'max_salary', 
            'requirements', 
            'application_deadline',
            'is_active'
        ]
        widgets = {
            'application_deadline': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 5}),
            'requirements': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'min_salary': 'Minimum Annual Salary ($)',
            'max_salary': 'Maximum Annual Salary ($)',
        }
