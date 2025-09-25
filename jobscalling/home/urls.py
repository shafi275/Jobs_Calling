from django.urls import path
from . import views

urlpatterns = [
    path("candidate/register/", views.candidate_register, name="candidate_register"),
    path("company/register/", views.company_register, name="company_register"),
    path("candidate/login/", views.candidate_login, name="candidate_login"),
    path("company/login/", views.company_login, name="company_login"),
]
