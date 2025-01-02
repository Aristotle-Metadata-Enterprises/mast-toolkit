"""
URL configuration for web project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from mast_toolkit import views

from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [
    path("create_survey", views.SurveyCreateView.as_view(), name="survey_create"),
    path("survey/manage/<survey_pk>", views.SurveyDetailView.as_view(), name="survey_dashboard"),
    path("survey/manage/<survey_pk>/responses", views.SurveyResponseListView.as_view(), name="survey_dashboard_responses"),
    path("survey/manage/<survey_pk>/report", views.SurveyReportDetailView.as_view(), name="survey_dashboard_report"),
    path("survey/manage/<survey_pk>/delete", views.SurveyDeleteView.as_view(), name="survey_dashboard_delete"),
    path("survey/manage/<survey_pk>/update", views.SurveyUpdateView.as_view(), name="survey_manage"),
    path("survey/manage/<survey_pk>/update/add_team", views.SurveyAddTeamView.as_view(), name="survey_manage_add_team"),
    path("survey/manage/<survey_pk>/update/delete_team/<team_pk>", views.SurveyDeleteTeamView.as_view(), name="survey_manage_delete_team"),
    # path("survey/dashboard/<survey_share_uuid>/", views.SurveyDeleteView.as_view(), name="survey_shared_dashboard"),
    # path("survey/dashboard/<survey_share_uuid>/report", views.SurveyDeleteView.as_view(), name="survey_shared_dashboard"),
    path("survey/response/<survey_pk>", views.ResponseCreateView.as_view(), name="survey_respond"),
    path("survey/response/<survey_pk>/thanks", views.ResponseThanksView.as_view(), name="survey_respond_thanks"),
    path("survey/deleted", TemplateView.as_view(template_name="mast/dashboard/delete_confirmation.html"), name="survey_deleted_confirmation"),
]
