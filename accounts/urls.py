from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'accounts'

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("login/", auth_views.LoginView.as_view(template_name='accounts/login.html', next_page='core:home'), name="login"),
    path('logout/', auth_views.LogoutView.as_view(next_page='accounts:login'), name='logout'),
]
