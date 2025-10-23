from django.views.generic import ListView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import FormView
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.contrib import messages
from accounts.models import ConnectionRequest, TherapistProfile
from .forms import ClientRegisterForm, ConnectionRequestForm, TherapistRegisterForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.http import JsonResponse # Ensure this import is present
from . import models # Ensure this import exists for load_provinces
from datetime import date
from django.views.generic import ListView
from accounts.models import TherapistProfile


class RegisterView(TemplateView):
    template_name = "accounts/register.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['client_form'] = ClientRegisterForm(prefix='client')
        context['therapist_form'] = TherapistRegisterForm(prefix='therapist')
        return context

    def post(self, request, *args, **kwargs):
        account_type = request.POST.get('account_type')

        if account_type == 'client':
            client_form = ClientRegisterForm(request.POST, prefix='client')
            therapist_form = TherapistRegisterForm(prefix='therapist')
            if client_form.is_valid():
                user = client_form.save()
                login(request, user)
                return redirect('core:home')
            else:
                context = {'client_form': client_form, 'therapist_form': therapist_form}
                return render(request, self.template_name, context)

        elif account_type == 'therapist':
            therapist_form = TherapistRegisterForm(request.POST, prefix='therapist')
            client_form = ClientRegisterForm(prefix='client')
            if therapist_form.is_valid():
                user = therapist_form.save()
                login(request, user)
                return redirect('core:home')
            else:
                context = {'client_form': client_form, 'therapist_form': therapist_form}
                return render(request, self.template_name, context)

        else:
            client_form = ClientRegisterForm(prefix='client')
            therapist_form = TherapistRegisterForm(prefix='therapist')
            context = {'client_form': client_form, 'therapist_form': therapist_form, 'error': 'Please select an account type.'}
            return render(request, self.template_name, context)

class TherapistListView(ListView):
    model = TherapistProfile
    template_name = "accounts/therapist_list.html"
    context_object_name = "therapists"

    def get_queryset(self):
        therapists = super().get_queryset()

        today = date.today()
        for t in therapists:
            if t.date_of_birth:
                t.age = today.year - t.date_of_birth.year - (
                    (today.month, today.day) < (t.date_of_birth.month, t.date_of_birth.day)
                )
        return therapists
        
class SendConnectionRequestView(LoginRequiredMixin, FormView):
    template_name = "accounts/send_request.html"
    form_class = ConnectionRequestForm
    success_url = reverse_lazy("accounts:client_dashboard")

    def form_valid(self, form):
        code = form.cleaned_data["therapist_code"].strip()
        client_profile = self.request.user.client_profile

        if client_profile.therapist:
            messages.error(self.request, "You already have a therapist.")
            return redirect(self.success_url)

        therapist = get_object_or_404(TherapistProfile, connection_code=code)

        existing_request = ConnectionRequest.objects.filter(
            client=client_profile,
            therapist=therapist,
            status__in=["pending", "accepted"]
        ).first()

        if existing_request:
            messages.warning(self.request, "You already sent a request to this therapist.")
            return redirect(self.success_url)

        ConnectionRequest.objects.create(client=client_profile, therapist=therapist)
        messages.success(self.request, "Connection request sent!")
        return super().form_valid(form)
    
class ConnectionRequestListView(LoginRequiredMixin, ListView):
    model = ConnectionRequest
    template_name = "accounts/therapist_requests.html"
    context_object_name = "requests"

    def get_queryset(self):
        therapist = self.request.user.therapist_profile
        return ConnectionRequest.objects.filter(therapist=therapist, status="pending").order_by("-created_at")

class AcceptConnectionRequestView(LoginRequiredMixin, View):
    def post(self, request, pk):
        therapist = request.user.therapist_profile
        connection_request = get_object_or_404(ConnectionRequest, pk=pk, therapist=therapist, status="pending")

        client_profile = connection_request.client
        client_profile.therapist = therapist
        client_profile.save()

        connection_request.status = "accepted"
        connection_request.save()

        messages.success(request, f"You are now connected with {client_profile.first_name}.")
        return redirect("accounts:therapist_requests")


class RejectConnectionRequestView(LoginRequiredMixin, View):
    def post(self, request, pk):
        therapist = request.user.therapist_profile
        connection_request = get_object_or_404(ConnectionRequest, pk=pk, therapist=therapist, status="pending")

        connection_request.status = "rejected"
        connection_request.save()

        messages.info(request, "Request rejected.")
        return redirect("accounts:therapist_requests")


@login_required
def dashboard_view(request):
    user = request.user

    if hasattr(user, "client_profile"):
        return render(request, "accounts/client_dashboard.html", {"user": user})
    elif hasattr(user, "therapist_profile"):
        return render(request, "accounts/therapist_dashboard.html", {"user": user})
    else:
        return redirect("accounts:register")
    
def load_provinces(request):
#Fetches the list of provinces/states for a selected country via AJAX."""
    country_code = request.GET.get('country')
    
    if country_code and country_code in models.REGION_DATA:
        regions = models.REGION_DATA[country_code]
        return JsonResponse(regions, safe=False)
        
    return JsonResponse([], safe=False)
    
