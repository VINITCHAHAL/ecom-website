from django import forms
from .models import User

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['name', 'password']

class ProductForm(forms.Form):
    name = forms.CharField(max_length=100)
    price = forms.DecimalField(max_digits=10, decimal_places=2)
    quantity = forms.IntegerField()
    product_image = forms.ImageField() 