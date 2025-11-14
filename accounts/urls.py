from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'accounts'

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    #path("login/", auth_views.LoginView.as_view(template_name='accounts/login.html', next_page='core:home'), name="login"),
    path('login/', views.login_view, name='login'),
    path("updateinfo/", views.update_info, name="update_info"),
    path('logout/', auth_views.LogoutView.as_view(next_page='accounts:login'), name='logout'),
    path("change-password/", views.CustomPasswordChangeView.as_view(), name="change_password"),
    path("send-request/", views.SendConnectionRequestViaCodeView.as_view(), name="send_connection_request"),
    path("therapist/requests/", views.ConnectionRequestListView.as_view(), name="therapist_requests"),
    path("therapist/requests/<int:pk>/accept/", views.AcceptConnectionRequestView.as_view(), name="accept_request"),
    path("therapist/requests/<int:pk>/reject/", views.RejectConnectionRequestView.as_view(), name="reject_request"),
    path("therapists/", views.TherapistListView.as_view(), name="therapist_list"),
    path("ajax/load_provinces/", views.load_provinces, name="ajax_load_provinces"),
    path('verify-2fa/', views.verify_2fa, name='verify_2fa'), #used for 2FA
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<str:token>/', views.reset_password_page, name='reset_password_page'),
    path('reset-password/<str:token>/submit/', views.reset_password_submit, name='reset_password_submit'),
    path("disconnect/<int:therapist_id>/", views.TherapistDisconnectView.as_view(), name="disconnect_therapist"),
    path('toggle-twofa/', views.toggle_twofa, name='toggle_twofa'),
    path('update-user-info/', views.UpdateUserInfoView.as_view(), name='update_user_info'),
    path("send-request/<int:therapist_id>/", views.SendDirectConnectionRequestView.as_view(), name="send_direct_request"),
]
