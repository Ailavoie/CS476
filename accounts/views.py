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
from .models import ConnectionRequest, ClientProfile, TherapistProfile

def reject_other_pending_requests(client_profile, accepted_therapist):
    """
    Finds and rejects all pending requests for a client_profile,
    """
    # 1. Find all PENDING requests for the given client
    pending_requests = ConnectionRequest.objects.filter(
        client=client_profile,
        status='pending'
    )

    # 2. Update their status to 'rejected'
    count = pending_requests.update(status='rejected')
    return count

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
        
        # 🌟 NEW LOGIC: Determine current client and their existing requests
        current_client_profile = None
        existing_requests_therapist_ids = set()

        # Check if the user is logged in and has a client profile
        if self.request.user.is_authenticated and hasattr(self.request.user, 'client_profile'):
            current_client_profile = self.request.user.client_profile
            
            # Get the IDs of all therapists the client has a pending/accepted request with
            existing_requests_therapist_ids = set(
                ConnectionRequest.objects
                .filter(client=current_client_profile, status__in=['pending', 'accepted'])
                .values_list('therapist_id', flat=True)
            )

        # 🌟 Iterate and annotate
        for t in therapists:
            # 1. Age calculation (existing logic)
            if t.date_of_birth:
                t.age = today.year - t.date_of_birth.year - (
                    (today.month, today.day) < (t.date_of_birth.month, t.date_of_birth.day)
                )

            # 2. Connection status check (NEW)
            t.has_pending_request = t.pk in existing_requests_therapist_ids
            
            # 3. Check if the client is already assigned to this therapist
            #    (This covers the 'accepted' status not in the ConnectionRequest table anymore)
            if current_client_profile and current_client_profile.therapist == t:
                t.is_connected = True
            else:
                t.is_connected = False

        return therapists

class SendDirectConnectionRequestView(LoginRequiredMixin, View):
    """
    Handles a direct connection request sent from the therapist list page.
    The therapist's ID (pk) is passed in the URL.
    """
    def post(self, request, pk):
        client_profile = request.user.client_profile
        
        # 1. Check if Client already has a therapist
        if client_profile.therapist:
            messages.error(request, "You already have a therapist. Please disconnect before sending a new request.")
            
            # 🌟 FIX HERE: Redirect back to the therapist list page (where the user is)
            return redirect("accounts:therapist_list") 

        # 2. Find the target therapist
        therapist = get_object_or_404(TherapistProfile, pk=pk)

        # 3. Check for existing pending/accepted request
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
            
            # Redirect back to the therapist list page
            return redirect("accounts:therapist_list")

        # 4. Create the new request
        ConnectionRequest.objects.create(client=client_profile, therapist=therapist)
        messages.success(request, f"Connection request sent to {therapist.first_name}!")
        
        # Redirect back to the list of therapists
        return redirect("accounts:therapist_list")

class SendConnectionRequestView(LoginRequiredMixin, FormView):
    template_name = "accounts/send_request.html"
    # Ensure ConnectionRequestForm is imported and correct
    form_class = ConnectionRequestForm 
    success_url = reverse_lazy("accounts:therapist_list") 

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

        # 2. Find the therapist (handles wrong code via form_invalid)
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
        
        # 🌟 FIX: Automatically reject all other pending requests 🌟
        # This is the crucial step to maintain one-to-one connections.
        reject_other_pending_requests(client_profile, therapist)
        
        # C. Send success message
        messages.success(self.request, f"You are now connected to {therapist.first_name} {therapist.last_name}.")
        
        # D. Stay on the same page
        return render(self.request, self.template_name, self.get_context_data(form=form))

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
        
        # 1. Establish the connection
        client_profile.therapist = therapist
        client_profile.save()

        # 2. Mark this request as accepted
        connection_request.status = "accepted"
        connection_request.save()
        
        # 🌟 FIX: Automatically reject all other pending requests
        reject_other_pending_requests(client_profile, therapist)

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
    
