from django import forms
from ebookapp.models import Address

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = [
            "full_name", "phone", "address_line1", "address_line2",
            "city", "state", "pincode", "country"
        ]
