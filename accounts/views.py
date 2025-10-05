from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from .forms import ClientRegisterForm, TherapistRegisterForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login

class RegisterView(TemplateView):
    template_name = "accounts/register.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['client_form'] = ClientRegisterForm()
        context['therapist_form'] = TherapistRegisterForm()
        return context

    def post(self, request, *args, **kwargs):
        account_type = request.POST.get('account_type')

        if account_type == 'client':
            client_form = ClientRegisterForm(request.POST)
            therapist_form = TherapistRegisterForm()
            if client_form.is_valid():
                user = client_form.save()
                login(request, user)
                return redirect('core:home')
            else:
                context = {'client_form': client_form, 'therapist_form': therapist_form}
                return render(request, self.template_name, context)

        elif account_type == 'therapist':
            therapist_form = TherapistRegisterForm(request.POST)
            client_form = ClientRegisterForm()
            if therapist_form.is_valid():
                user = therapist_form.save()
                login(request, user)
                return redirect('core:home')
            else:
                context = {'client_form': client_form, 'therapist_form': therapist_form}
                return render(request, self.template_name, context)

        else:
            client_form = ClientRegisterForm()
            therapist_form = TherapistRegisterForm()
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