from django import forms
from django.contrib import admin
from .models import BotDiagnoses, DiagnosticCorrector
from core.chatbot.models import DiagnosticCorrector
from core.my_admin.admin import my_admin_site
from core.healthcare.admin import my_doctor_site



class DiagnosticCorrectorAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs  # Superusers can see all diagnostic corrections

        # Filter diagnostic corrections based on the related booking's doctor
        return qs.filter(bot_diagnosis__booking__doctor=request.user)

class BotDiagnosisForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['readonly'] = True
    class Meta:
        model = BotDiagnoses
        fields = '__all__'

class InlineDiagnosticCorrector(admin.StackedInline):
    model = DiagnosticCorrector
    extra = 0  # Show only one instance

class BotDiagnosisAdmin(admin.ModelAdmin):
    inlines = [InlineDiagnosticCorrector]
    form = BotDiagnosisForm
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing instance
            return self.readonly_fields + ('symptoms_group', 'diagnosis', 'diagnosis_date', 'diagnosis_time', 'subject')
        return self.readonly_fields



#admin site
my_admin_site.register(BotDiagnoses)
my_admin_site.register(DiagnosticCorrector)


#doctor site
my_doctor_site.register(BotDiagnoses, BotDiagnosisAdmin)
my_doctor_site.register(DiagnosticCorrector, DiagnosticCorrectorAdmin)
# my_doctor_site.register(DiagnosticCorrector)
