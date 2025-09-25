from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from .models import CandidateProfile, CompanyProfile
from django.contrib.auth import authenticate, login

# Candidate Registration
def candidate_register(request):
    if request.method == "POST":
        full_name = request.POST.get("fullName")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirmPassword")
        terms = request.POST.get("terms")

        # Check password match
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("candidate_register")

        # Create User
        if User.objects.filter(username=email).exists():
            messages.error(request, "Email already registered.")
            return redirect("candidate_register")

        user = User.objects.create(
            username=email,
            email=email,
            password=make_password(password),
        )

        # Candidate profile
        CandidateProfile.objects.create(
            user=user,
            full_name=full_name,
            agree_terms=True if terms else False,
        )

        messages.success(request, "Registration successful! Please login.")
        return redirect("candidate_login")

    return render(request, "candidate_register.html")


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
        confirm_password = request.POST.get("confirmPassword")
        terms = request.POST.get("terms")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("company_register")

        if User.objects.filter(username=email).exists():
            messages.error(request, "Email already registered.")
            return redirect("company_register")

        user = User.objects.create(
            username=email,
            email=email,
            password=make_password(password),
        )

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
        return redirect("login")

    return render(request, "company_register.html")
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
            return redirect("CandidateDashboard.html")  # replace with your dashboard route
        else:
            messages.error(request, "Invalid email or password.")
            return redirect("candidate_login")

    return render(request, "CandidateLogin.html")
def company_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Authenticate using email as username
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Company logged in successfully!")
            return redirect("CompanyDahboard.html")  # Replace with your company dashboard URL
        else:
            messages.error(request, "Invalid email or password.")
            return redirect("company_login")

    return render(request, "CompanyLogin.html")

def landing_page(request):
    return render(request, "landing.html")  

def common_signup(request):
    return render(request, "CommonSignUp.html")