from django import forms
from .models import Profile
from django.contrib.auth.forms import PasswordChangeForm


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['display_name', 'phone_number', 'id_document_type','profile_pic']

    # Add custom validation if needed (for example, checking for duplicate phone number)


class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Profile
        fields = ['old_password', 'new_password1', 'new_password2']
