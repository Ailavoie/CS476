from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from .forms import ClientRegisterForm, TherapistRegisterForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.http import JsonResponse # Ensure this import is present
from . import models # Ensure this import exists for load_provinces

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
    