from django.urls import path
from . import views
urlpatterns = [
    path("", views.home, name="home"),
    path("contact/", views.contact, name="contact"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("portal/<str:portal>/", views.portal, name="portal"),
    path("modules/<str:slug>/", views.module_list, name="module_list"),
    path("modules/<str:slug>/add/", views.module_create, name="module_create"),
    path("modules/<str:slug>/<int:pk>/edit/", views.module_edit, name="module_edit"),
    path("modules/<str:slug>/<int:pk>/delete/", views.module_delete, name="module_delete"),
    path("leads/new/", views.public_lead, name="public_lead"),
    path("reports/", views.reports, name="reports"),
    path("reports/export.csv", views.export_csv, name="export_csv"),
    path("insights/", views.insights, name="insights"),
    path("backup/", views.backup_page, name="backup"),
    path("backup/download/", views.backup_download, name="backup_download"),
    path("audio/upload/", views.audio_upload, name="audio_upload"),
    path("audio/", views.audio_list, name="audio_list"),
]
