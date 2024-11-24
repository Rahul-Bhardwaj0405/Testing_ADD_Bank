from django import forms
from .models import BankDetails

class BankDetailsForm(forms.ModelForm):
    MERCHANT_NAME_CHOICES = [
        ('', 'Select'),
        ('IRCTC WEB', 'IRCTC WEB'),
        ('IRCTC APP', 'IRCTC APP'),
        ('IRCTC AIR TICKET', 'IRCTC AIR TICKET'),
        ('IRCTC TOURISM', 'IRCTC TOURISM'),
        ('ALL', 'ALL'),
    ]

    TRANSACTION_TYPE_CHOICES = [
        ('', 'Select'),
        ('SALE', 'SALE'),
        ('REFUND', 'REFUND'),
        ('NET SETTLED', 'NET SETTLED'),
    ]

    merchant_name = forms.ChoiceField(
        choices=MERCHANT_NAME_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    transaction_type = forms.ChoiceField(
        choices=TRANSACTION_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    class Meta:
        model = BankDetails
        fields = ['bank_name', 'bank_id', 'mid', 'merchant_name', 'transaction_type']
        widgets = {
            'bank_name': forms.TextInput(attrs={'class': 'form-control'}),
            'bank_id': forms.TextInput(attrs={'class': 'form-control'}),
            'mid': forms.TextInput(attrs={'class': 'form-control'}),
        }