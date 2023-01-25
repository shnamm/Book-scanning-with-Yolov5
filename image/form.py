from django import forms
from .dmodels import Image

class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields=("caption", "image", "title")