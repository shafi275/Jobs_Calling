from django.db import models
from django.contrib.auth.models import User

# Candidate Profile (extra info)
class CandidateProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=150)
    agree_terms = models.BooleanField(default=False)

    def __str__(self):
        return self.full_name
    
class CompanyProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=200)
    industry = models.CharField(max_length=100)
    company_size = models.CharField(max_length=50)
    contact_person = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=20)
    website = models.URLField(blank=True, null=True)
    agree_terms = models.BooleanField(default=False)

    def __str__(self):
        return self.company_name