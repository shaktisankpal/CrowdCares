from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, InvestorProfile, FundraiserProfile, NGOWelfareProfile, FundraisingProject, NGODonationPost

class UserRegistrationForm(UserCreationForm):
    user_type = forms.ChoiceField(choices=User.USER_TYPES, label="User Type")

    # Profile fields, all optional by default
    full_name = forms.CharField(max_length=255, required=False)
    phone_number = forms.CharField(max_length=15, required=False)
    govt_id = forms.CharField(max_length=50, required=False)
    bank_account_details = forms.CharField(widget=forms.Textarea, required=False)

    # Investor-specific fields
    organization = forms.CharField(max_length=255, required=False)
    job_title = forms.CharField(max_length=255, required=False)
    country = forms.CharField(max_length=100, required=False)
    city = forms.CharField(max_length=100, required=False)

    # NGO-specific fields
    organization_name = forms.CharField(max_length=255, required=False)
    darpan_id = forms.CharField(max_length=50, required=False)
    address = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = User
        fields = ["username", "email", "user_type", "password1", "password2"]

    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get('user_type')

        if user_type == 'investor':
            required_fields = ['full_name', 'phone_number', 'country', 'city', 'govt_id', 'bank_account_details']
            for field in required_fields:
                if not cleaned_data.get(field):
                    self.add_error(field, f'This field is required for investors.')
        
        elif user_type == 'fundraiser':
            required_fields = ['full_name', 'phone_number', 'govt_id', 'bank_account_details']
            for field in required_fields:
                if not cleaned_data.get(field):
                    self.add_error(field, f'This field is required for fundraisers.')
        
        elif user_type == 'ngo':
            required_fields = ['organization_name', 'darpan_id', 'phone_number', 'address', 'bank_account_details']
            for field in required_fields:
                if not cleaned_data.get(field):
                    self.add_error(field, f'This field is required for NGOs.')

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            if user.user_type == "investor":
                InvestorProfile.objects.create(
                    user=user,
                    full_name=self.cleaned_data.get("full_name"),
                    phone_number=self.cleaned_data.get("phone_number"),
                    organization=self.cleaned_data.get("organization"),
                    job_title=self.cleaned_data.get("job_title"),
                    country=self.cleaned_data.get("country"),
                    city=self.cleaned_data.get("city"),
                    govt_id=self.cleaned_data.get("govt_id"),
                    bank_account_details=self.cleaned_data.get("bank_account_details"),
                )
            elif user.user_type == "fundraiser":
                FundraiserProfile.objects.create(
                    user=user,
                    full_name=self.cleaned_data.get("full_name"),
                    phone_number=self.cleaned_data.get("phone_number"),
                    govt_id=self.cleaned_data.get("govt_id"),
                    bank_account_details=self.cleaned_data.get("bank_account_details"),
                )
            elif user.user_type == "ngo":
                NGOWelfareProfile.objects.create(
                    user=user,
                    organization_name=self.cleaned_data.get("organization_name"),
                    darpan_id=self.cleaned_data.get("darpan_id"),
                    phone_number=self.cleaned_data.get("phone_number"),
                    address=self.cleaned_data.get("address"),
                    bank_account_details=self.cleaned_data.get("bank_account_details"),
                )
        return user
    
class FundraisingProjectForm(forms.ModelForm):
    class Meta:
        model = FundraisingProject
        fields = [
            'title', 'category', 'description', 'goal_amount', 'min_contribution',
            'start_date', 'end_date', 'story_media_link', 'social_media_links', 'reward_tiers'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

class NGODonationPostForm(forms.ModelForm):
    class Meta:
        model = NGODonationPost
        fields = [
            'title', 'category', 'description', 'beneficiaries', 'supporting_documents',
            'target_amount', 'min_contribution', 'start_date', 'end_date', 'social_media_links'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }