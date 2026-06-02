from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import HouseholdMembership, Profile, User

class CustomUserCreationForm(UserCreationForm):
    """Registration form based on Django's safe password-handling form."""

    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-input')

    def clean_email(self):
        # clean_email runs during form.is_valid() and prevents duplicate accounts.
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ('username', 'password')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-input')


class ProfileForm(forms.ModelForm):
    """Profile editor that accepts comma-separated text for JSON list fields."""

    allergies_text = forms.CharField(required=False, help_text='Separate values with commas')
    likes_text = forms.CharField(required=False, help_text='Separate values with commas')
    dislikes_text = forms.CharField(required=False, help_text='Separate values with commas')

    class Meta:
        model = Profile
        fields = (
            'diet_type',
            'calorie_goal',
            'protein_goal',
            'carbs_goal',
            'fat_goal',
            'weekly_budget_xaf',
            'timezone',
            'measurement_system',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['allergies_text'].initial = ', '.join(self.instance.allergies)
            self.fields['likes_text'].initial = ', '.join(self.instance.likes)
            self.fields['dislikes_text'].initial = ', '.join(self.instance.dislikes)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-input')

    def save(self, commit=True):
        # Convert text boxes into JSON lists before saving the Profile model.
        profile = super().save(commit=False)
        profile.allergies = self._split('allergies_text')
        profile.likes = self._split('likes_text')
        profile.dislikes = self._split('dislikes_text')
        if commit:
            profile.save()
            profile.user.allergies = profile.allergies
            profile.user.dietary_preferences = profile.preference_summary()
            profile.user.save(update_fields=['allergies', 'dietary_preferences'])
        return profile

    def _split(self, field_name):
        value = self.cleaned_data.get(field_name, '')
        items = [item.strip().lower()[:80] for item in value.split(',') if item.strip()]
        return items[:30]


class HouseholdInviteForm(forms.Form):
    """Simple non-model form for adding an existing user to a household."""

    username = forms.CharField(max_length=150)
    role = forms.ChoiceField(choices=HouseholdMembership.Role.choices)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-input')
