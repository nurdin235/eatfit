from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.views.decorators.http import require_POST
from django_ratelimit.decorators import ratelimit
from .forms import CustomUserCreationForm, CustomAuthenticationForm, HouseholdInviteForm, ProfileForm
from .models import HouseholdMembership, Profile
from .services import add_member_by_username, get_active_household, user_role

@ratelimit(key='ip', rate='5/m', method='POST', block=True)
def register_view(request):
    """Create a new user, household, profile, and logged-in session."""

    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Every registered user immediately gets a household for scoped data.
            user.ensure_household()
            Profile.objects.get_or_create(user=user)
            login(request, user)
            messages.success(request, "Registration successful. Welcome to EatFit!")
            return redirect('dashboard')
        else:
            messages.error(request, "Unsuccessful registration. Invalid information.")
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'auth/register.html', {'form': form})

@ratelimit(key='ip', rate='10/m', method='POST', block=True)
@ratelimit(key='post:username', rate='5/m', method='POST', block=True)
def login_view(request):
    """Authenticate a user and store their login in the session."""

    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if request.POST.get('remember-me') == 'on':
                    request.session.set_expiry(60 * 60 * 24 * 14)
                else:
                    request.session.set_expiry(0)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = CustomAuthenticationForm()
        
    return render(request, 'auth/login.html', {'form': form})

@require_POST
@login_required
def logout_view(request):
    """Clear the session so the browser is no longer authenticated."""

    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('auth:login')


@login_required
def profile_view(request):
    """Display and save the current user's profile preferences."""

    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated. Meal planning will use these preferences.")
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'users/profile.html', {'form': form, 'profile': profile})


@login_required
def household_view(request):
    """Show household members and let owners add existing users."""

    household = get_active_household(request.user)
    role = user_role(request.user, household)
    invite_form = HouseholdInviteForm()

    if request.method == 'POST':
        # Only owners and superusers can change household membership.
        if role != HouseholdMembership.Role.OWNER and not request.user.is_superuser:
            raise PermissionDenied("Only household owners can invite members.")
        invite_form = HouseholdInviteForm(request.POST)
        if invite_form.is_valid():
            try:
                add_member_by_username(
                    household,
                    invite_form.cleaned_data['username'],
                    invite_form.cleaned_data['role'],
                )
                messages.success(request, "Household member added.")
                return redirect('households')
            except Exception:
                messages.error(request, "Could not add that user. Check the username and try again.")

    memberships = household.memberships.select_related('user').order_by('role', 'user__username')
    return render(
        request,
        'users/household.html',
        {'household': household, 'memberships': memberships, 'role': role, 'invite_form': invite_form},
    )
