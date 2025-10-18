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
        context['client_form'] = ClientRegisterForm()
        context['therapist_form'] = TherapistRegisterForm()
        # Set a default initial tab for the first load
        context['initial_tab'] = 'client' 
        return context

    def post(self, request, *args, **kwargs):
        account_type = request.POST.get('account_type')
        
        # Determine the initial tab based on the submission attempt
        initial_tab = account_type if account_type in ['client', 'therapist'] else 'client'

        if account_type == 'client':
            client_form = ClientRegisterForm(request.POST)
            # NOTE: Instantiate the other form empty so it renders but doesn't validate
            therapist_form = TherapistRegisterForm() 
            if client_form.is_valid():
                user = client_form.save()
                login(request, user)
                return redirect('core:home')
            else:
                # CRITICAL: Pass client_form with errors and the active tab
                context = {'client_form': client_form, 'therapist_form': therapist_form, 'initial_tab': initial_tab}
                return render(request, self.template_name, context)

        elif account_type == 'therapist':
            therapist_form = TherapistRegisterForm(request.POST)
            client_form = ClientRegisterForm() # Instantiate empty
            if therapist_form.is_valid():
                user = therapist_form.save()
                login(request, user)
                return redirect('core:home')
            else:
                # CRITICAL: Pass therapist_form with errors and the active tab
                context = {'client_form': client_form, 'therapist_form': therapist_form, 'initial_tab': initial_tab}
                return render(request, self.template_name, context)

        else:
            client_form = ClientRegisterForm()
            therapist_form = TherapistRegisterForm()
            context = {'client_form': client_form, 'therapist_form': therapist_form, 'error': 'Please select an account type.', 'initial_tab': initial_tab}
            return render(request, self.template_name, context)

# --- Helper Functions ---

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
    """Fetches the list of provinces/states for a selected country via AJAX."""
    country_code = request.GET.get('country')
    
    if country_code and country_code in models.REGION_DATA:
        regions = models.REGION_DATA[country_code]
        return JsonResponse(regions, safe=False)
        
    return JsonResponse([], safe=False)