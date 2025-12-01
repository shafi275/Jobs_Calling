from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from .models import CandidateProfile, CompanyProfile
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError # Needed for unique_together constraint
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count

# Import models and form
from .models import CandidateProfile, CompanyProfile, JobPosting, JobApplication, CandidateResume, Review
from .forms import JobPostingForm # Assumes you have created this form


# Candidate Registration
def candidate_register(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        terms = request.POST.get("terms")

        # Check password match
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("candidate_register")

        # Check if email already exists
        if User.objects.filter(username=email).exists():
            messages.error(request, "Email already registered.")
            return redirect("candidate_register")

        # Create user
        user = User.objects.create(
            username=email ,
            first_name=full_name ,
            email=email,
            password=make_password(password),
        )

        # Create candidate profile
        CandidateProfile.objects.create(
            user=user,
            full_name=full_name,
            agree_terms=True if terms else False,
        )

        # after successful creation:
        messages.success(request, "Registered successfully. Please sign in.")
        return redirect('/candidate/login/')

    return render(request, "CandidateRegistration.html")


# Company Registration
def company_register(request):
    if request.method == "POST":
        company_name = request.POST.get("companyName")
        industry = request.POST.get("industry")
        company_size = request.POST.get("companySize")
        email = request.POST.get("companyEmail")
        contact_person = request.POST.get("contactPerson")
        phone_number = request.POST.get("phoneNumber")
        website = request.POST.get("website")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        terms = request.POST.get("terms")

        # Check password match
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("company_register")

        # Check if email already exists
        if User.objects.filter(username=email).exists():
            messages.error(request, "Email already registered.")
            return redirect("company_register")

        # Create user
        user = User.objects.create(
            username=email,
            email=email,
            first_name=company_name, 
            password=make_password(password),
        )

        # Create company profile
        CompanyProfile.objects.create(
            user=user,
            company_name=company_name,
            industry=industry,
            company_size=company_size,
            contact_person=contact_person,
            phone_number=phone_number,
            website=website,
            agree_terms=True if terms else False,
        )

        messages.success(request, "Company registered! Please login.")
        return redirect('/company/login/')  # explicit path; preserves existing UI


    return render(request, "CompanyRegistration.html")


# Candidate Login
def candidate_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Authenticate using email as username
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Logged in successfully!")
            return redirect('/candidate/dashboard/')
        else:
            messages.error(request, "Invalid email or password.")
            return redirect("candidate_login")

    return render(request, "CandidateLogin.html")


# Company Login
def company_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Authenticate using email as username
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Company logged in successfully!")
            return redirect('/company/dashboard/')
        else:
            messages.error(request, "Invalid email or password.")
            return redirect("company_login")

    return render(request, "CompanyLogin.html")


# Landing Page
def landing_page(request):
    # Prepare testimonials for landing page (students and companies)
    student_reviews = Review.objects.filter(is_active=True, reviewer_type='student').order_by('-created_at')[:6]
    company_reviews = Review.objects.filter(is_active=True, reviewer_type='company').order_by('-created_at')[:6]
    # Detect if user is logged-in and their profile type to auto-set reviewer type
    user_reviewer_type = None
    try:
        if request.user.is_authenticated:
            if CandidateProfile.objects.filter(user=request.user).exists():
                user_reviewer_type = 'student'
            elif CompanyProfile.objects.filter(user=request.user).exists():
                user_reviewer_type = 'company'
    except Exception:
        user_reviewer_type = None

    context = {
        'student_reviews': student_reviews,
        'company_reviews': company_reviews,
        'user_reviewer_type': user_reviewer_type,
    }
    return render(request, "landing.html", context)


def submit_review(request):
    # Accepts POST submissions from landing page review form (anonymous allowed)
    if request.method == 'POST':
        name = request.POST.get('name', '').strip() or 'Anonymous'
        company = request.POST.get('company', '').strip() or None
        rating = int(request.POST.get('rating', 5)) if request.POST.get('rating') else 5
        review_text = request.POST.get('review', '').strip()
        # If reviewer_type provided (optional) else default to 'student'
        reviewer_type = request.POST.get('reviewer_type', 'student')
        # sanitize reviewer type
        if reviewer_type not in ('student', 'company'):
            reviewer_type = 'student'

        # If user is logged-in and wants to explicitly confirm their profile type, we still keep
        # the posted value. However, we can log or enforce policy if desired.

        if not review_text:
            from django.contrib import messages
            messages.error(request, 'Please provide a short review text before submitting.')
            return redirect('landing_page')

        # Create review; mark active True so it appears immediately in success stories
        Review.objects.create(
            name=name,
            company=company,
            rating=max(1, min(5, rating)),
            review=review_text,
            reviewer_type=reviewer_type,
            is_active=True
        )
        from django.contrib import messages
        messages.success(request, 'Thank you for your review! It is now shown on the site under Success Stories.')
        return redirect('landing_page')
    # Non-POST - redirect to landing
    return redirect('landing_page')


# Common Sign Up Page (choose Student/Company)
def common_signup(request):
    return render(request, "CommonSignUp.html")


# Candidate Dashboard (login required)
@login_required
def candidate_dashboard(request):
    # Provide active job postings to the candidate dashboard so real jobs are shown
    from .models import JobPosting
    job_qs = JobPosting.objects.filter(is_active=True).select_related('company').annotate(app_count=Count('applications')).order_by('-posted_date')

    # Paginate candidate dashboard jobs (10 per page)
    paginator = Paginator(job_qs, 10)
    page = request.GET.get('page', 1)
    try:
        jobs_page = paginator.page(page)
    except PageNotAnInteger:
        jobs_page = paginator.page(1)
    except EmptyPage:
        jobs_page = paginator.page(paginator.num_pages)

    context = {
        'jobs': jobs_page,  # Page object usable like an iterable in templates
        'paginator': paginator,
        'page_obj': jobs_page,
    }
    return render(request, "CandidateDashboard.html", context)

# Candidate Profile (view)
@login_required
def candidate_profile(request):
    # Load candidate profile if exists
    try:
        profile = CandidateProfile.objects.get(user=request.user)
    except CandidateProfile.DoesNotExist:
        profile = None
    return render(request, "CandidateProfile.html", {"profile": profile})

@login_required
def candidate_cv(request):
    # Ensure candidate profile exists
    try:
        candidate_profile = CandidateProfile.objects.get(user=request.user)
    except CandidateProfile.DoesNotExist:
        messages.error(request, "Candidate profile not found. Please complete your profile first.")
        return redirect('candidate_dashboard')

    if request.method == 'POST':
        uploaded_file = request.FILES.get('cvFile')
        if not uploaded_file:
            messages.error(request, "Please select a file to upload.")
            return redirect('candidate_cv')

        # Validation
        MAX_SIZE = 5 * 1024 * 1024  # 5 MB
        allowed_types = [
            'application/pdf',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        ]

        if uploaded_file.size > MAX_SIZE:
            messages.error(request, "File too large. Maximum allowed size is 5MB.")
            return redirect('candidate_cv')

        if uploaded_file.content_type not in allowed_types:
            messages.error(request, "Invalid file type. Only PDF and DOCX are allowed.")
            return redirect('candidate_cv')

        # Save resume record
        resume = CandidateResume.objects.create(
            candidate=candidate_profile,
            file=uploaded_file,
            original_filename=getattr(uploaded_file, 'name', ''),
            content_type=getattr(uploaded_file, 'content_type', ''),
            file_size=getattr(uploaded_file, 'size', None)
        )
        messages.success(request, "Your CV was uploaded successfully.")
        return redirect('candidate_profile')

    return render(request, "UploadCV.html")
# Company Dashboard (login required)
@login_required
def company_dashboard(request):
    # Try to load company profile and recent jobs for display on the dashboard
    recent_jobs = []
    try:
        company_profile = CompanyProfile.objects.get(user=request.user)
        recent_jobs = JobPosting.objects.filter(company=company_profile).order_by('-posted_date')[:5]
    except CompanyProfile.DoesNotExist:
        company_profile = None

    return render(request, "CompanyDashboard.html", {"recent_jobs": recent_jobs})


@login_required
def post_job(request):
    """
    Allows a logged-in company user to post a new job.
    """
    try:
        # 1. Ensure the user is associated with a CompanyProfile
        company_profile = CompanyProfile.objects.get(user=request.user)
    except CompanyProfile.DoesNotExist:
        messages.error(request, "You must have a Company Profile to post jobs.")
        return redirect('company_dashboard') 

    if request.method == 'POST':
        # Use JobPostingForm (which should be defined in forms.py)
        form = JobPostingForm(request.POST)
        if form.is_valid():
            # 2. Save the form data, but don't commit yet
            job = form.save(commit=False)
            # 3. Assign the JobPosting to the logged-in company
            job.company = company_profile

            # Support edit mode if 'id' provided (via query param or hidden field)
            edit_id = request.POST.get('id') or request.GET.get('id')
            if edit_id:
                try:
                    existing = JobPosting.objects.get(pk=edit_id, company=company_profile)
                    # Update fields from the form-cleaned data
                    existing.title = job.title
                    existing.description = job.description
                    existing.location = job.location
                    existing.job_type = job.job_type
                    existing.min_salary = job.min_salary
                    existing.max_salary = job.max_salary
                    existing.requirements = job.requirements
                    existing.application_deadline = job.application_deadline
                    existing.is_active = job.is_active
                    existing.save()
                    messages.success(request, f"Job '{existing.title}' updated successfully!")
                    return redirect('company_job_list')
                except JobPosting.DoesNotExist:
                    # Fallthrough to create as new if not found
                    pass

            # Server-side duplicate prevention: same company, same title and location
            title_clean = (job.title or '').strip()
            location_clean = (job.location or '').strip()
            dup_qs = JobPosting.objects.filter(
                company=company_profile,
                title__iexact=title_clean,
                location__iexact=location_clean
            )
            if dup_qs.exists():
                # If a duplicate exists, warn and don't create another
                messages.warning(request, "A similar job already exists. Please modify the title or location if you intended to post a different role.")
                return redirect('company_job_list')

            # Save new job and send a single success message
            job.save()
            messages.success(request, f"Job '{job.title}' posted successfully!")
            return redirect('company_job_list') # Redirect to the list of jobs
    else:
        form = JobPostingForm()

    context = {
        'form': form,
        'is_new_job': True,
    }
    return render(request, 'PostJob.html', context)


@login_required
def company_job_list(request):
    """
    Lists all job postings created by the logged-in company.
    """
    try:
        company_profile = CompanyProfile.objects.get(user=request.user)
    except CompanyProfile.DoesNotExist:
        messages.error(request, "You must be a registered company to view your job list.")
        return redirect('company_dashboard')

    # Fetch all job postings for the current company and annotate application counts
    job_qs = JobPosting.objects.filter(company=company_profile).annotate(app_count=Count('applications')).order_by('-posted_date')

    # Paginate results (10 per page)
    paginator = Paginator(job_qs, 10)
    page = request.GET.get('page', 1)
    try:
        jobs_page = paginator.page(page)
    except PageNotAnInteger:
        jobs_page = paginator.page(1)
    except EmptyPage:
        jobs_page = paginator.page(paginator.num_pages)

    context = {
        'job_list': jobs_page,
        'company_name': company_profile.company_name,
        'paginator': paginator,
        'page_obj': jobs_page,
    }
    return render(request, 'CompanyJobListing.html', context)


@login_required
def job_detail(request, pk):
    """
    Displays the details of a specific job posting.
    Accessible by both candidates (to apply) and companies (to review).
    """
    job = get_object_or_404(JobPosting, pk=pk)
    
    # Determine user role
    is_candidate = CandidateProfile.objects.filter(user=request.user).exists()
    is_company_owner = False
    has_applied = False
    
    if is_candidate:
        candidate_profile = CandidateProfile.objects.get(user=request.user)
        # Check if candidate has already applied
        has_applied = JobApplication.objects.filter(job=job, candidate=candidate_profile).exists()
    else:
        # Check if the logged-in user is the company owner
        try:
            company_profile = CompanyProfile.objects.get(user=request.user)
            if job.company == company_profile:
                is_company_owner = True
        except CompanyProfile.DoesNotExist:
            pass # Not a company user

    context = {
        'job': job,
        'is_company_owner': is_company_owner,
        'is_candidate': is_candidate,
        'has_applied': has_applied,
    }

    return render(request, 'JobDetail.html', context)
    
    
@login_required
def apply_for_job(request, job_id):
    """
    Allows a candidate to apply for a specific job posting.
    Extended to handle additional job application details.
    """
    job = get_object_or_404(JobPosting, pk=job_id)

    try:
        candidate_profile = CandidateProfile.objects.get(user=request.user)
    except CandidateProfile.DoesNotExist:
        messages.error(request, "You must be logged in as a Candidate to apply for jobs.")
        return redirect('job_detail', pk=job_id)

    # Handle form submission
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        dob = request.POST.get('dob', None)
        education = request.POST.get('education', '')
        experience = request.POST.get('experience', '')
        expected_salary = request.POST.get('expected_salary', '')
        skills = request.POST.get('skills', '')
        portfolio = request.POST.get('portfolio', '')
        cover_letter = request.POST.get('cover_letter', '')

        resume = request.FILES.get('resume', None)  # Handle uploaded file

        try:
            # Prevent duplicate applications
            if JobApplication.objects.filter(job=job, candidate=candidate_profile).exists():
                messages.warning(request, f"You have already applied for '{job.title}'.")
                return redirect('job_detail', pk=job_id)

            JobApplication.objects.create(
                job=job,
                candidate=candidate_profile,
                full_name=full_name,
                email=email,
                phone=phone,
                dob=dob,
                education=education,
                experience=experience,
                expected_salary=expected_salary,
                skills=skills,
                portfolio=portfolio,
                cover_letter=cover_letter,
                resume=resume
            )

            messages.success(request, f"Successfully applied for '{job.title}'!")
            return redirect('candidate_dashboard')

        except IntegrityError:
            messages.warning(request, f"You have already applied for '{job.title}'.")
            return redirect('job_detail', pk=job_id)
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
            return redirect('job_detail', pk=job_id)

    # If GET → show the form
    return render(request, 'ApplyJob.html', {'job': job})

@login_required
def view_applicants(request, job_id):
    """
    Show all applicants who applied for a specific job.
    Only accessible by the company who posted the job.
    """
    try:
        company_profile = CompanyProfile.objects.get(user=request.user)
    except CompanyProfile.DoesNotExist:
        messages.error(request, "You must be logged in as a company to view applicants.")
        return redirect('home')

    job = get_object_or_404(JobPosting, id=job_id, company=company_profile)
    applicants = JobApplication.objects.filter(job=job).select_related('candidate')

    context = {
        'company': company_profile,
        'job': job,
        'applicants': applicants,
    }
    return render(request, 'view_applicants.html', context)

@login_required
def application_detail(request, application_id):
    """
    Show full details of a specific application.
    Accessible only by the company who owns the job.
    """
    try:
        company_profile = CompanyProfile.objects.get(user=request.user)
    except CompanyProfile.DoesNotExist:
        messages.error(request, "You must be logged in as a company to view application details.")
        return redirect('home')

    application = get_object_or_404(
        JobApplication,
        id=application_id,
        job__company=company_profile
    )

    context = {
        'application': application,
        'job': application.job,
    }
    return render(request, 'application_detail.html', context)
