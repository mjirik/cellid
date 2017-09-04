from django import forms
from .models import ImageQuatro


class DocumentForm(forms.ModelForm):
    class Meta:
        model = ImageQuatro
        fields = ('description', 'multicell_fitc', "multicell_dapi", "singlecell_fitc", "singlecell_dapi", )