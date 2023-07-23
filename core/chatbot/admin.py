from django import forms
from django.contrib import admin
from .models import BotDiagnoses, DiagnosticCorrector, ChatbotSettings
from core.chatbot.models import DiagnosticCorrector
from core.my_admin.admin import my_admin_site
from core.healthcare.admin import my_doctor_site
from django.apps import apps

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
            return self.readonly_fields + ('user_case', 'symptoms_group', 'diagnosis', 'diagnosis_date', 'diagnosis_time', 'subject')
        return self.readonly_fields
    


class ChatbotSettingsAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        self.reload_models()

    def reload_models(self):
        app_config = apps.get_app_config('chatbot')
        app_config.reload_models()



#admin site
my_admin_site.register(BotDiagnoses)
my_admin_site.register(DiagnosticCorrector)
my_admin_site.register(ChatbotSettings, ChatbotSettingsAdmin)


#doctor site
my_doctor_site.register(BotDiagnoses, BotDiagnosisAdmin)
my_doctor_site.register(DiagnosticCorrector)
# my_doctor_site.register(DiagnosticCorrector)
