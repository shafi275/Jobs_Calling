from django.urls import path
from . import views

urlpatterns = [
    path("candidate/register/", views.candidate_register, name="candidate_register"),
    path("company/register/", views.company_register, name="company_register"),
]
