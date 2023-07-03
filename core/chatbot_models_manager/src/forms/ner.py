
from django import forms
from ...models import NER

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
