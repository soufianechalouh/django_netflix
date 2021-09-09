from django import forms

from .models import RatingChoices


class RatingForm(forms.Form):
    rating = forms.ChoiceField(choices=RatingChoices.choices)
    object_id = forms.IntegerField(widget=forms.HiddenInput)
    content_type_id = forms.IntegerField(widget=forms.HiddenInput)
    next = forms.CharField(widget=forms.HiddenInput)
