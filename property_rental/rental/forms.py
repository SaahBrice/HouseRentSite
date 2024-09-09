from django import forms
from .models import Visitor, BookingReservation, Rating

class VisitorRegistrationForm(forms.ModelForm):
    confirm_access_code = forms.CharField(max_length=4, label="Confirmer le code d'accès")

    class Meta:
        model = Visitor
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'address', 'sex', 'bio', 'access_code']

    def clean_access_code(self):
        access_code = self.cleaned_data.get('access_code')
        if len(access_code) != 4 or not access_code.isalnum():
            raise forms.ValidationError("Le code d'accès doit contenir exactement 4 caractères alphanumériques.")
        return access_code

    def clean(self):
        cleaned_data = super().clean()
        access_code = cleaned_data.get('access_code')
        confirm_access_code = cleaned_data.get('confirm_access_code')

        if access_code and confirm_access_code and access_code != confirm_access_code:
            raise forms.ValidationError("Les codes d'accès ne correspondent pas.")

class BookingForm(forms.ModelForm):
    class Meta:
        model = BookingReservation
        fields = ['booking_reason']
        widgets = {
            'booking_reason': forms.Textarea(attrs={'rows': 4}),
        }

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4}),
        }