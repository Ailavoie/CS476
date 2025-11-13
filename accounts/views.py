from django.views.generic import ListView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import FormView
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView
from django.contrib import messages
from accounts.models import ConnectionRequest, TherapistProfile
from .forms import ClientRegisterForm, ConnectionRequestForm, TherapistRegisterForm, UpdateClientInfoForm, UpdateUserInfoForm, UpdateTherapistInfoForm
from accounts.models import ConnectionRequest, TherapistProfile, ClientProfile
from .forms import ClientRegisterForm, ConnectionRequestForm, TherapistRegisterForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.http import JsonResponse # Ensure this import is present
from . import models # Ensure this import exists for load_provinces
from datetime import date
from django.views.generic import ListView
from accounts.models import TherapistProfile
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .models import TwoFactorCode
from django.contrib.auth import get_user_model
import json
from django.views.decorators.http import require_POST
from django.contrib.auth.views import PasswordChangeView

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
                # Specify backend when logging in after registration
                login(request, user, backend='accounts.backends.EmailBackend')
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
                # Specify backend when logging in after registration
                login(request, user, backend='accounts.backends.EmailBackend')
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
    
#2FA

def login_view(request):
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        print("="*50)
        print("LOGIN ATTEMPT")
        print("Is AJAX:", is_ajax)
        print("Headers:", dict(request.headers))
        print("POST data:", request.POST)
        print("="*50)
        
        # Get email and password from POST data
        email = request.POST.get('username')
        password = request.POST.get('password')
        
        print(f"Email: {email}")
        print(f"Password exists: {password is not None and len(password) > 0}")
        
        if not email or not password:
            if is_ajax:
                return JsonResponse({'success': False, 'error': 'Email and password required'})
            else:
                form = AuthenticationForm()
                return render(request, 'accounts/login.html', {'form': form})
        
        # Authenticate using email and password
        user = authenticate(request, username=email, password=password)
        
        print(f"Authenticated user: {user}")
        
        # ONLY proceed if user credentials are valid
        if user is not None:
            # User credentials are VALID - they exist in the database and password matches
            print("✓ Authentication successful - user credentials are valid")
            
            # CHECK IF USER HAS 2FA ENABLED
            twofa_enabled = False
            
            # Check if user is a client with 2FA enabled
            if hasattr(user, 'client_profile') and user.client_profile.twofa:
                twofa_enabled = True
                print("Client has 2FA enabled")
            
            # Check if user is a therapist with 2FA enabled
            elif hasattr(user, 'therapist_profile') and user.therapist_profile.twofa:
                twofa_enabled = True
                print("Therapist has 2FA enabled")
            
            # If 2FA is ENABLED, send code and require verification
            if twofa_enabled:
                # Generate 2FA code
                code = TwoFactorCode.generate_code()
                TwoFactorCode.objects.create(user=user, code=code)
                
                print(f"Generated 2FA code: {code}")
                
                # Send email with code
                try:
                    send_mail(
                        subject='Your 2FA Code',
                        message=f'Your verification code is: {code}\n\nThis code will expire in 10 minutes.',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                        fail_silently=False,
                    )
                    print(f"2FA code sent to {user.email}: {code}")
                except Exception as e:
                    print(f"Email sending failed: {e}")
                
                # Store user id in session for 2FA verification
                request.session['pending_user_id'] = user.id
                
                print("RETURNING JSON: success=True, requires_2fa=True")
                
                if is_ajax:
                    return JsonResponse({'success': True, 'requires_2fa': True})
                else:
                    return render(request, 'accounts/login.html', {
                        'show_2fa': True,
                        'form': AuthenticationForm()
                    })
            
            # If 2FA is DISABLED, log them in directly
            else:
                print("2FA is disabled - logging user in directly")
                
                # Log the user in immediately
                login(request, user, backend='accounts.backends.EmailBackend')
                
                print("SUCCESS: User logged in without 2FA")
                
                if is_ajax:
                    return JsonResponse({'success': True, 'requires_2fa': False})
                else:
                    return redirect('core:home')
        else:
            # User credentials are INVALID
            print("✗ Authentication FAILED - invalid email or password")
            
            if is_ajax:
                return JsonResponse({
                    'success': False, 
                    'error': 'Invalid email or password'
                })
            else:
                form = AuthenticationForm()
                return render(request, 'accounts/login.html', {
                    'form': form,
                    'error': 'Invalid email or password'
                })
    else:
        # GET request - show login form
        print("GET request - rendering login form")
        form = AuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})

def verify_2fa(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            code = data.get('code')
            user_id = request.session.get('pending_user_id')
            
            print("="*50)
            print("2FA VERIFICATION ATTEMPT")
            print(f"Code entered: {code}")
            print(f"User ID from session: {user_id}")
            print("="*50)
            
            if not user_id:
                print("ERROR: No pending_user_id in session")
                return JsonResponse({'success': False, 'error': 'No pending authentication'})
            
            # Get the most recent unused code for this user
            try:
                all_codes = TwoFactorCode.objects.filter(user_id=user_id).order_by('-created_at')
                print(f"Found {all_codes.count()} total codes for user {user_id}")
                for c in all_codes[:3]:  # Show last 3 codes
                    print(f"  Code: {c.code}, Used: {c.is_used}, Valid: {c.is_valid()}, Created: {c.created_at}")
                
                two_fa_code = TwoFactorCode.objects.filter(
                    user_id=user_id,
                    code=code,
                    is_used=False
                ).latest('created_at')
                
                print(f"Found matching code: {two_fa_code.code}")
                print(f"Code is valid: {two_fa_code.is_valid()}")
                
                if two_fa_code.is_valid():
                    two_fa_code.is_used = True
                    two_fa_code.save()
                    
                    # Log the user in - specify the backend
                    User = get_user_model()
                    user = User.objects.get(id=user_id)
                    
                    # Specify the backend explicitly
                    login(request, user, backend='accounts.backends.EmailBackend')
                    
                    # Clean up session
                    del request.session['pending_user_id']
                    
                    print("SUCCESS: User logged in")
                    return JsonResponse({'success': True})
                else:
                    print("ERROR: Code expired")
                    return JsonResponse({'success': False, 'error': 'Code expired'})
            except TwoFactorCode.DoesNotExist:
                print("ERROR: Code not found in database")
                return JsonResponse({'success': False, 'error': 'Invalid code'})
        except json.JSONDecodeError:
            print("ERROR: Invalid JSON in request body")
            return JsonResponse({'success': False, 'error': 'Invalid request format'})
        except Exception as e:
            print(f"ERROR: Unexpected error: {e}")
            return JsonResponse({'success': False, 'error': 'An error occurred'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

#password reset

def forgot_password(request):
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        email = request.POST.get('email')
        
        print("="*50)
        print("PASSWORD RESET REQUEST")
        print(f"Email: {email}")
        print("="*50)
        
        if not email:
            if is_ajax:
                return JsonResponse({'success': False, 'error': 'Email is required'})
        
        # Check if user exists
        User = get_user_model()
        
        try:
            user = User.objects.get(email=email)
            
            # Generate reset token
            token = TwoFactorCode.generate_token()
            TwoFactorCode.objects.create(
                user=user,
                token=token,
                code_type='password_reset'
            )
            
            # Create reset link
            reset_link = request.build_absolute_uri(
                f'/accounts/reset-password/{token}/'
            )
            
            # Send email
            try:
                send_mail(
                    subject='Password Reset Request',
                    message=f'Click the link below to reset your password:\n\n{reset_link}\n\nThis link will expire in 1 hour.\n\nIf you did not request this, please ignore this email.',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
                print(f"Reset link sent to {user.email}: {reset_link}")
            except Exception as e:
                print(f"Email sending failed: {e}")
            
            if is_ajax:
                return JsonResponse({'success': True, 'message': 'Password reset link sent to your email'})
        except User.DoesNotExist:
            # Don't reveal if email exists or not (security)
            if is_ajax:
                return JsonResponse({'success': True, 'message': 'If that email exists, a reset link has been sent'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})


def reset_password_page(request, token):
    """Display the password reset form"""
    # Verify token is valid
    try:
        reset_code = TwoFactorCode.objects.get(
            token=token,
            code_type='password_reset',
            is_used=False
        )
        
        if not reset_code.is_valid():
            return render(request, 'accounts/reset_password.html', {
                'error': 'This reset link has expired. Please request a new one.',
                'token_valid': False
            })
        
        return render(request, 'accounts/reset_password.html', {
            'token': token,
            'token_valid': True
        })
    except TwoFactorCode.DoesNotExist:
        return render(request, 'accounts/reset_password.html', {
            'error': 'Invalid reset link.',
            'token_valid': False
        })


def reset_password_submit(request, token):
    """Handle the password reset form submission"""
    if request.method == 'POST':
        new_password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if new_password != confirm_password:
            return render(request, 'accounts/reset_password.html', {
                'token': token,
                'token_valid': True,
                'error': 'Passwords do not match'
            })
        
        # Validate password strength (reuse your existing validation)
        if len(new_password) < 6:
            return render(request, 'accounts/reset_password.html', {
                'token': token,
                'token_valid': True,
                'error': 'Password must be at least 6 characters'
            })
        
        try:
            reset_code = TwoFactorCode.objects.get(
                token=token,
                code_type='password_reset',
                is_used=False
            )
            
            if not reset_code.is_valid():
                return render(request, 'accounts/reset_password.html', {
                    'error': 'This reset link has expired.',
                    'token_valid': False
                })
            
            # Update password
            user = reset_code.user
            user.set_password(new_password)
            user.save()
            
            # Mark token as used
            reset_code.is_used = True
            reset_code.save()
            
            messages.success(request, 'Password reset successful! You can now log in.')
            return redirect('accounts:login')
            
        except TwoFactorCode.DoesNotExist:
            return render(request, 'accounts/reset_password.html', {
                'error': 'Invalid reset link.',
                'token_valid': False
            })
    
    return redirect('accounts:login')
def update_info(request):
    user = request.user

    if hasattr(user, "client_profile"):
        return render(request, "accounts/client_update_info.html", {"user": user})
    elif hasattr(user, "therapist_profile"):
        return render(request, "accounts/therapist_update_info.html", {"user": user})
    else:
        return redirect("accounts:register")

#A post method is required to call this function
@require_POST
def toggle_twofa(request):
    #the user is stored
    user = request.user

    #if the user is a client
    if hasattr(user, "client_profile"):
        client = request.user.client_profile
        #twofa field is updated to the opposite
        client.twofa = not client.twofa
        #new twofa field is saved
        client.save()
        print("Saved client 2FA:", client.twofa)
        #json is returned to update view
        return JsonResponse({'twofa': client.twofa})
    #if the user is a therapist
    else:
        therapist = request.user.therapist_profile
        #twofa field is updated to the opposite
        therapist.twofa = not therapist.twofa
        #new twofa field is saved
        therapist.save()
        print("Saved therapist 2FA:", therapist.twofa)
        #json is returned to update view
        return JsonResponse({'twofa': therapist.twofa})
    
#Login required for this view. View is for updating the user's info    
@login_required
def update_user_info(request):
    #user is set
    user = request.user
    #if profile is set based off if a user has a client_profile or a therapist_profile
    profile = user.client_profile if hasattr(user, "client_profile") else user.therapist_profile if hasattr(user, "therapist_profile") else None
    print(profile)
    
    #If there is a post method
    if request.method == 'POST':

        #If the user has a client profile the UpdateClientInfoForm class is called
        if hasattr(user, "client_profile"):
            profile_form = UpdateClientInfoForm(request.POST, instance=profile)
        #If the user has a therapist profile the UpdateTherapistInfoForm class is called
        elif hasattr(user, "therapist_profile"):
            profile_form = UpdateTherapistInfoForm(request.POST, instance=profile)

        #if the form has no errors save the form and redirect
        if profile_form.is_valid()  :
            profile_form.save()
            messages.success(request, "Your changes have been saved.")
            return redirect('accounts:update_user_info')
        else:
            return redirect('accounts:update_user_info')
    #If it is not a post method fill the fields with current data
    else:
        #user_form is used for the email field
        user_form = UpdateUserInfoForm(instance=user)

        #if the user is a client show client fields
        if hasattr(user, "client_profile"):
            profile_form = UpdateClientInfoForm(instance=profile)
        #if the user is a therapist show therapist fields
        elif hasattr(user, "therapist_profile"):
            profile_form = UpdateTherapistInfoForm(instance=profile)
        #if neither redirect to registration
        else:
            return redirect("accounts:register")
        
        #render the html with the field data
        return render(request, "accounts/update_user_info.html", {
            "user_form": user_form,
            "profile_form": profile_form,
            })

#view for customizing the PasswordChangeView
class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    #update the template
    template_name = 'accounts/change_password.html'
    #update the success url page
    success_url = reverse_lazy('accounts:update_info')

    #add a success message upon password change
    def form_valid(self, form):
        messages.success(self.request, "Your password has been changed successfully!")
        return super().form_valid(form)
