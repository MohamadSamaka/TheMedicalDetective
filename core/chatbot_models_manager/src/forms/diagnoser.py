
from django import forms
from ...models import Diagnoser

class DiagnoserInfoForm(forms.ModelForm):
    neurons_first_layer = forms.IntegerField(
        label="layer 1 # of neurons",
        initial=64,
        min_value= 64,
        
    )
    neurons_second_layer = forms.IntegerField(
        label="layer 2 # of neurons",
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
    
    testing_file = forms.FileField(
        label="Testing file",
        required=True,
    )

    class Meta:
        model = Diagnoser
        fields = '__all__'  # Or specify the fields you want to include
