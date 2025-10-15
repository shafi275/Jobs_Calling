from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator


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
    
class JobPosting(models.Model):
    """
    Represents a single job advertisement posted by a company.
    """
    # Relationship: A CompanyProfile can post multiple jobs.
    company = models.ForeignKey(
        CompanyProfile,
        on_delete=models.CASCADE,
        related_name='job_postings',
        help_text="The company that posted this job."
    )

    # Core Job Details
    title = models.CharField(max_length=255, help_text="The job title (e.g., 'Senior Python Developer')")
    description = models.TextField(help_text="Detailed description of the role.")
    location = models.CharField(max_length=100, help_text="City, State, or 'Remote'")
    
    # Job Type Choices
    JOB_TYPES = [
        ('FT', 'Full-time'),
        ('PT', 'Part-time'),
        ('CT', 'Contract'),
        ('IT', 'Internship'),
    ]
    job_type = models.CharField(
        max_length=2,
        choices=JOB_TYPES,
        default='FT',
        help_text="Type of employment."
    )

    # Salary fields (using IntegerField for easier filtering/sorting)
    min_salary = models.IntegerField(
        null=True, 
        blank=True, 
        validators=[MinValueValidator(0)],
        help_text="Minimum expected annual salary (optional)."
    )
    max_salary = models.IntegerField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Maximum expected annual salary (optional)."
    )

    # Requirements/Skills
    requirements = models.TextField(help_text="Key skills and qualifications required (e.g., technologies, education).")

    # Status and Dates
    posted_date = models.DateTimeField(auto_now_add=True)
    application_deadline = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True, help_text="Is this job currently accepting applications?")

    class Meta:
        ordering = ['-posted_date']
        verbose_name_plural = "Job Postings"

    def __str__(self):
        return f"{self.title} at {self.company.company_name}"


class JobApplication(models.Model):
    """
    Tracks a specific application by a candidate to a specific job posting.
    """
    # Relationship: Many applications can be for one job, and many applications can be made by one candidate.
    job = models.ForeignKey(
        JobPosting, 
        on_delete=models.CASCADE, 
        related_name='applications',
        help_text="The job posting the candidate is applying for."
    )
    candidate = models.ForeignKey(
        CandidateProfile, 
        on_delete=models.CASCADE, 
        related_name='applications',
        help_text="The candidate submitting the application."
    )
    
    application_date = models.DateTimeField(auto_now_add=True)
    cover_letter = models.TextField(blank=True, null=True)

    # Application Status Choices
    STATUS_CHOICES = [
        ('PENDING', 'Pending Review'),
        ('REVIEWED', 'Reviewed'),
        ('INTERVIEW', 'Interview Scheduled'),
        ('OFFER', 'Offer Extended'),
        ('HIRED', 'Hired'),
        ('REJECTED', 'Rejected'),
    ]
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='PENDING',
        help_text="Current status of the application."
    )
    
    # In a real app, you would likely use a FileField here for resume/CV upload.
    # resume_file = models.FileField(upload_to='resumes/', null=True, blank=True)

    class Meta:
        # Prevent the same candidate from applying to the same job twice
        unique_together = ('job', 'candidate') 
        ordering = ['-application_date']
        verbose_name_plural = "Job Applications"

    def __str__(self):
        return f"{self.candidate.full_name}'s application for {self.job.title}"


class CandidateResume(models.Model):
    """
    Stores uploaded CVs/resumes for candidates.
    """
    candidate = models.ForeignKey(
        CandidateProfile,
        on_delete=models.CASCADE,
        related_name='resumes',
        help_text="Candidate who uploaded this resume."
    )
    file = models.FileField(upload_to='resumes/')
    original_filename = models.CharField(max_length=255, blank=True)
    content_type = models.CharField(max_length=100, blank=True)
    file_size = models.PositiveIntegerField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Candidate Resume'
        verbose_name_plural = 'Candidate Resumes'

    def __str__(self):
        return f"{self.candidate.full_name} - {self.original_filename or self.file.name}"
