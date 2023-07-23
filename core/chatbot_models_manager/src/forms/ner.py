
from django import forms
from ...models import NER
from core.core.src.utls.helpers import validate_model_filename

class NERInfoForm(forms.ModelForm):
    neurons_first_layer = forms.IntegerField(
        label="layer 1 # of neurons",
        initial=64,
        min_value= 64,
    )
    iterations = forms.IntegerField(
        label="# of iterations",
        initial=100,
        min_value= 100,
    )

    training_file = forms.FileField(
        label="Training file",
        required=True,
    )

    class Meta:
        model = NER
        fields = '__all__' 

    def clean_model_name(self):
        filename = self.cleaned_data.get('model_name')
        if filename:
            if not validate_model_filename(filename):
                raise forms.ValidationError('Invalid filename. Only letters (uppercase and lowercase), underscore symbols, and numbers are allowed.')
        return filename