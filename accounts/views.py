from django.views.generic import ListView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import FormView
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView
from django.contrib import messages
from accounts.models import ConnectionRequest, TherapistProfile, ClientProfile
from .forms import ClientRegisterForm, ConnectionRequestForm, TherapistRegisterForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.http import JsonResponse # Ensure this import is present
from . import models # Ensure this import exists for load_provinces
from datetime import date
from django.views.generic import ListView

def delete_other_pending_requests(client_profile, accepted_therapist):
    """
    Finds and rejects all pending requests for a client_profile,
    """
    # 1. Find all PENDING requests for the given client
    pending_requests = ConnectionRequest.objects.filter(
        client=client_profile,
        status='pending'
    ).exclude(therapist=accepted_therapist)

    count, _ = pending_requests.delete()  # Django returns (num_deleted, dict)
    return count

class RegisterView(TemplateView):
    template_name = "accounts/register.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['client_form'] = ClientRegisterForm(prefix='client')
        context['therapist_form'] = TherapistRegisterForm(prefix='therapist')
        context['initial_tab'] = kwargs.get('initial_tab', 'client')
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
                context = {
                    'client_form': client_form,
                    'therapist_form': therapist_form,
                    'initial_tab': 'client'
                }
                return render(request, self.template_name, context)

        elif account_type == 'therapist':
            therapist_form = TherapistRegisterForm(request.POST, prefix='therapist')
            client_form = ClientRegisterForm(prefix='client')
            if therapist_form.is_valid():
                user = therapist_form.save()
                login(request, user)
                return redirect('core:home')
            else:
                context = {
                    'client_form': client_form,
                    'therapist_form': therapist_form,
                    'initial_tab': 'therapist'
                }
                return render(request, self.template_name, context)

        else:
            client_form = ClientRegisterForm(prefix='client')
            therapist_form = TherapistRegisterForm(prefix='therapist')
            context = {
                'client_form': client_form,
                'therapist_form': therapist_form,
                'initial_tab': 'client',
                'error': 'Please select an account type.'
            }
            return render(request, self.template_name, context)

class TherapistListView(ListView):
    model = TherapistProfile
    template_name = "accounts/therapist_list.html"
    context_object_name = "therapists"

    def get_queryset(self):
        therapists = super().get_queryset()
        today = date.today()

        current_client_profile = None
        existing_requests_therapist_ids = set()

        # Check if the user is logged in and has a client profile
        if self.request.user.is_authenticated and hasattr(self.request.user, 'client_profile'):
            current_client_profile = self.request.user.client_profile

            # IDs of therapists with pending or accepted requests
            existing_requests_therapist_ids = set(
                ConnectionRequest.objects
                .filter(client=current_client_profile, status__in=['pending', 'accepted'])
                .values_list('therapist_id', flat=True)
            )

        for t in therapists:
            # Age calculation
            if t.date_of_birth:
                t.age = today.year - t.date_of_birth.year - (
                    (today.month, today.day) < (t.date_of_birth.month, t.date_of_birth.day)
                )

            # Connection flags
            t.has_pending_request = t.pk in existing_requests_therapist_ids
            t.is_connected = current_client_profile and current_client_profile.therapist == t

        return therapists

class SendConnectionRequestViaCodeView(LoginRequiredMixin, FormView):
    template_name = "accounts/send_request.html"
    form_class = ConnectionRequestForm
    success_url = reverse_lazy("accounts:therapist_list")  # Adjust if needed

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_invalid(self, form):
        messages.error(self.request, "The connection code is invalid or not found.")
        return render(self.request, self.template_name, self.get_context_data(form=form))

    def form_valid(self, form):
        code = form.cleaned_data["therapist_code"].strip()
        client_profile = self.request.user.client_profile

        # 1. Check if client already has ANY therapist assigned
        if client_profile.therapist:
            messages.error(self.request, "You already have a therapist.")
            return render(self.request, self.template_name, self.get_context_data(form=form)) 

        # 2. Find the therapist
        try:
            therapist = TherapistProfile.objects.get(connection_code=code)
        except TherapistProfile.DoesNotExist:
            return self.form_invalid(form) 

        # --- Connection Established (Automatic Acceptance Logic) ---

        # A. Assign the therapist
        client_profile.therapist = therapist
        client_profile.save()

        # B. Create the ConnectionRequest entry with 'accepted' status
        ConnectionRequest.objects.create(
            client=client_profile, 
            therapist=therapist, 
            status="accepted"
        )

        # C. Automatically reject all other pending requests
        delete_other_pending_requests(client_profile, therapist)

        # D. Send success message
        messages.success(self.request, f"You are now connected to {therapist.first_name} {therapist.last_name}.")

        # E. Render the same page (or redirect if you prefer)
        # return render(self.request, self.template_name, self.get_context_data(form=form))
        return redirect('accounts:therapist_list')

class ConnectionRequestListView(LoginRequiredMixin, ListView):
    model = ConnectionRequest
    template_name = "accounts/therapist_requests.html"
    context_object_name = "requests"

    def get_queryset(self):
        therapist = self.request.user.therapist_profile
        return ConnectionRequest.objects.filter(
            therapist=therapist, status="pending"
        ).order_by("-created_at")

class AcceptConnectionRequestView(LoginRequiredMixin, View):
    def post(self, request, pk):
        therapist = request.user.therapist_profile
        connection_request = get_object_or_404(
            ConnectionRequest, pk=pk, therapist=therapist, status="pending"
        )

        client_profile = connection_request.client
        client_profile.therapist = therapist
        client_profile.save()

        connection_request.status = "accepted"
        connection_request.save()

        messages.success(request, f"You are now connected with {client_profile.user.first_name}.")
        delete_other_pending_requests(client_profile, therapist)
        return redirect("accounts:therapist_requests")

class RejectConnectionRequestView(LoginRequiredMixin, View):
    def post(self, request, pk):
        therapist = request.user.therapist_profile
        connection_request = get_object_or_404(
            ConnectionRequest, pk=pk, therapist=therapist, status="pending"
        )

        connection_request.status = "rejected"
        connection_request.save()

        messages.info(request, "Request rejected.")
        return redirect("accounts:therapist_requests")

class TherapistDisconnectView(LoginRequiredMixin, View):
    """
    Handles client disconnection from therapist.
    If the request includes ?next=therapist-list or ?next=send-request, 
    it redirects back to the appropriate page.
    """
    # success_url is only used as a default fallback now
    success_url = reverse_lazy("accounts:dashboard") 

    def get_object(self):
        therapist_id = self.kwargs.get("therapist_id")
        return get_object_or_404(TherapistProfile, id=therapist_id)

    def post(self, request, therapist_id):
        client_profile = request.user.client_profile
        therapist = self.get_object()

        # --- Determine the final redirect URL ---
        next_page = request.GET.get("next")
        
        if next_page == "therapist-list":
            # New condition: Redirect to the therapist list
            redirect_target = reverse("accounts:therapist_list")
        else:
            # Default fallback: Redirect to the dashboard
            redirect_target = self.success_url
        # ----------------------------------------

        if not client_profile.therapist:
            messages.error(request, "You are not currently connected with any therapist.")
            # Use the determined redirect target
            return redirect(redirect_target)

        if client_profile.therapist != therapist:
            messages.error(request, "You are not connected with this therapist.")
            # Use the determined redirect target
            return redirect(redirect_target)

        # 1. Disconnect the client
        client_profile.therapist = None
        client_profile.save()

        # 2. Update the connection request status
        ConnectionRequest.objects.filter(
            client=client_profile,
            therapist=therapist,
            status="accepted"
        ).update(status="disconnected")

        messages.success(request, "You have successfully disconnected from your therapist.")
        # Final redirection
        return redirect(redirect_target)

class SendDirectConnectionRequestView(LoginRequiredMixin, View):
    """
    Handles sending a direct connection request to a therapist
    without requiring an access code.
    """
    success_url = reverse_lazy("accounts:therapist_list")

    def post(self, request, therapist_id):
        client_profile = request.user.client_profile
        therapist = get_object_or_404(TherapistProfile, id=therapist_id)

        # 1. Check if client already has a therapist
        if client_profile.therapist:
            if client_profile.therapist == therapist:
                messages.warning(request, "You are already connected with this therapist.")
            else:
                messages.error(request, "You already have a therapist. Disconnect before sending a new request.")
            return redirect(self.success_url)

        # 2. Check for existing pending/accepted request to the same therapist
        existing_request = ConnectionRequest.objects.filter(
            client=client_profile,
            therapist=therapist,
            status__in=["pending", "accepted"]
        ).first()

        if existing_request:
            if existing_request.status == "accepted":
                messages.warning(request, "You are already connected with this therapist.")
            else:
                messages.warning(request, "You already sent a pending request to this therapist.")
            return redirect(self.success_url)

        # 3. Create a new pending connection request
        ConnectionRequest.objects.create(
            client=client_profile,
            therapist=therapist,
            status="pending"
        )

        messages.success(request, f"Connection request sent to {therapist.first_name} {therapist.last_name}.")
        return redirect(self.success_url)

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
    
