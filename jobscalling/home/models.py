from django.db import models
from django.contrib.auth.models import User

# Candidate Profile (extra info)
class CandidateProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=150)
    agree_terms = models.BooleanField(default=False)

    def __str__(self):
        return self.full_name
