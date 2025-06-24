from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import modelformset_factory
from phonenumber_field.formfields import PhoneNumberField
from .models import User, DealerProfile, DealerPrice, DealerInquiry, ScrapMaterial

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone_number = PhoneNumberField(required=False, region='IN')
    user_type = forms.ChoiceField(choices=User.USER_TYPES, initial='regular')
    city = forms.CharField(max_length=100, required=False)
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone_number', 
                 'user_type', 'city', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Username'})
        self.fields['first_name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'First Name'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Last Name'})
        self.fields['email'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Email'})
        self.fields['phone_number'].widget.attrs.update({'class': 'form-control', 'placeholder': '+91 9876543210'})
        self.fields['city'].widget.attrs.update({'class': 'form-control', 'placeholder': 'City'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm Password'})

class DealerRegistrationForm(forms.ModelForm):
    class Meta:
        model = DealerProfile
        fields = [
            'business_name', 'business_registration_number', 'gst_number',
            'business_address', 'business_phone', 'business_email', 'website',
            'years_in_business', 'specialization', 'minimum_quantity',
            'pickup_available', 'delivery_available', 'operating_hours',
            'business_license'
        ]
        widgets = {
            'business_address': forms.Textarea(attrs={'rows': 3}),
            'specialization': forms.Textarea(attrs={'rows': 3}),
            'operating_hours': forms.TextInput(attrs={'placeholder': 'e.g., Mon-Sat 9AM-6PM'}),
            'minimum_quantity': forms.TextInput(attrs={'placeholder': 'e.g., 50kg minimum'}),
            'website': forms.URLInput(attrs={'placeholder': 'https://yourwebsite.com'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field not in ['pickup_available', 'delivery_available']:
                self.fields[field].widget.attrs.update({'class': 'form-control'})

class DealerPriceForm(forms.ModelForm):
    class Meta:
        model = DealerPrice
        fields = ['material', 'quality_grade', 'price_per_unit', 'minimum_quantity', 'is_active']
        widgets = {
            'price_per_unit': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'minimum_quantity': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }

# Create a formset for managing multiple prices
DealerPriceFormSet = modelformset_factory(
    DealerPrice,
    form=DealerPriceForm,
    extra=3,
    can_delete=True
)

class DealerInquiryForm(forms.ModelForm):
    class Meta:
        model = DealerInquiry
        fields = ['material', 'subject', 'message', 'quantity', 'contact_preference']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4}),
            'quantity': forms.TextInput(attrs={'placeholder': 'e.g., 100kg'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['material'].queryset = ScrapMaterial.objects.filter(is_active=True)
        self.fields['material'].required = False
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

class PriceSearchForm(forms.Form):
    material = forms.ModelChoiceField(
        queryset=ScrapMaterial.objects.filter(is_active=True),
        empty_label="Select Material",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    quality_grade = forms.ChoiceField(
        choices=ScrapMaterial.QUALITY_GRADES,
        initial='A',
        widget=forms.Select(attrs={'class': 'form-control'})
    )