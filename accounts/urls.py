from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'accounts'

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("login/", auth_views.LoginView.as_view(template_name='accounts/login.html', next_page='core:home'), name="login"),
    path('logout/', auth_views.LogoutView.as_view(next_page='accounts:login'), name='logout'),
    path("send-request/", views.SendConnectionRequestView.as_view(), name="send_connection_request"),
    path("therapist/requests/", views.ConnectionRequestListView.as_view(), name="therapist_requests"),
    path("therapist/requests/<int:pk>/accept/", views.AcceptConnectionRequestView.as_view(), name="accept_request"),
    path("therapist/requests/<int:pk>/reject/", views.RejectConnectionRequestView.as_view(), name="reject_request"),
    path("therapists/", views.TherapistListView.as_view(), name="therapist_list"),
    path("ajax/load_provinces/", views.load_provinces, name="ajax_load_provinces"),
    path("disconnect/<int:therapist_id>/", views.TherapistDisconnectView.as_view(), name="disconnect_therapist"),
]
