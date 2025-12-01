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
    Includes applicant details and additional fields.
    """
    # Relationships
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

    # Extended applicant details (from the form)
    full_name = models.CharField(max_length=100,default="", help_text="Full name of the applicant.")
    email = models.EmailField(default="",help_text="Applicant's email address.")
    phone = models.CharField(max_length=20,default="", help_text="Applicant's phone number.")
    dob = models.DateField(null=True, blank=True, help_text="Date of birth of the applicant.")
    education = models.CharField(max_length=200, blank=True, help_text="Highest education qualification.")
    experience = models.CharField(max_length=50, blank=True, help_text="Years of experience (e.g., 2 years, 6 months).")
    expected_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Expected salary in BDT.")
    skills = models.TextField(blank=True, help_text="Skills or technologies known by the applicant.")
    portfolio = models.URLField(blank=True, help_text="Link to LinkedIn or portfolio (optional).")

    # Application fields
    cover_letter = models.TextField(blank=True, null=True)
    resume = models.FileField(upload_to='resumes/', null=True, blank=True, help_text="Uploaded resume file.")
    application_date = models.DateTimeField(auto_now_add=True)

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

    class Meta:
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


class Review(models.Model):
    REVIEWER_TYPES = [
        ('student', 'Student'),
        ('company', 'Company'),
    ]
    name = models.CharField(max_length=150)
    company = models.CharField(max_length=200, blank=True, null=True)
    rating = models.PositiveSmallIntegerField(default=5)
    review = models.TextField()
    reviewer_type = models.CharField(max_length=20, choices=REVIEWER_TYPES, default='student')
    is_active = models.BooleanField(default=True, help_text='Show this review on the landing page')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'

    def __str__(self):
        return f"{self.name} - {self.company or self.reviewer_type}"
