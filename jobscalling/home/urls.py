from django.urls import path
from . import views

urlpatterns = [
    path("", views.landing_page, name="landing_page"),
    path('signup/', views.common_signup, name='common_signup'),
    path("candidate/register/", views.candidate_register, name="candidate_register"),
    path("company/register/", views.company_register, name="company_register"),
    path("candidate/login/", views.candidate_login, name="candidate_login"),
    path("company/login/", views.company_login, name="company_login"),
   path('candidate/dashboard/', views.candidate_dashboard, name='candidate_dashboard'),
    path('candidate/upload-cv/', views.candidate_cv, name='candidate_cv'),
    path('candidate/profile/', views.candidate_profile, name='candidate_profile'),
    path('company/dashboard/', views.company_dashboard, name='company_dashboard'),
    # Job posting and management
    path('company/post-job/', views.post_job, name='post_job'),
    path('company/jobs/', views.company_job_list, name='company_job_list'),
    path('jobs/<int:pk>/', views.job_detail, name='job_detail'),
    path('jobs/<int:job_id>/apply/', views.apply_for_job, name='apply_job'),
    path('submit-review/', views.submit_review, name='submit_review'),
    path('company/jobs/<int:job_id>/applicants/', views.view_applicants, name='view_applicants'),
    path('company/application/<int:application_id>/', views.application_detail, name='application_detail'),


]    
