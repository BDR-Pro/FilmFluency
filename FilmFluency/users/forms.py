from django import forms
from .models import UserProfile

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['nickname', 'profile_picture', 'bio', 'language', 'country']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control'}),
            'nickname': forms.TextInput(attrs={'class': 'form-control'}),
            'language': forms.Select(attrs={'class': 'form-control'}),
            'country': forms.Select(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control-file'}),
        }


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')
    referred_by = forms.ModelChoiceField(
        queryset=UserProfile.objects.exclude(referral_code__isnull=True).exclude(referral_code__exact=''),
        to_field_name="referral_code",
        required=False,
        help_text='Enter the referral code of the user who referred you.'
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Create the user profile if it doesn't exist
            referred_by = self.cleaned_data.get('referred_by')
            UserProfile.objects.get_or_create(user=user, defaults={'referred_by': referred_by})
        return user