from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView

from django.http import JsonResponse
from django.db import transaction
from core.my_admin.models import CustomUser
from core.healthcare.models import DoctorsInformation, UsersMeicalRecord, Diseases, Hospitals, Specializations
import random

class ChatbotView(TemplateView):
    template_name = 'client/pages/chatbot.html'

    responses = {
        "greeting": ["Hello! How can I assist you today?", "Hi there! How may I help you with your medical concern?"],
        "symptom_extraction": ["Thank you for sharing your explanation. Let me analyze it to extract relevant symptoms.", "I'll analyze your explanation to identify the symptoms you mentioned."],
        "prediction": ["Based on the symptoms you provided, it appears that you might have [predicted disease].", "After analyzing your symptoms, it seems likely that you have [predicted disease]."],
        "recommendation": ["Considering your symptoms, I recommend you consult a specialist at [recommended hospital] for further evaluation and treatment.", "For further evaluation and treatment, I suggest you visit [recommended hospital] and consult a specialist."],
        "additional_info": ["If you have any other symptoms or questions, please let me know.", "Feel free to share any additional symptoms or ask any questions you have."],
        "farewell": ["I hope I was able to assist you. Remember, it's always best to consult a healthcare professional for a proper diagnosis and treatment.", "Take care, and if you have any more questions in the future, don't hesitate to reach out."]
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = {'url_name': self.request.resolver_match.url_name}
        context['greeting'] = self.get_random_response('greeting')
        context['url_name'] = self.request.resolver_match.app_name
        print("appname!: ", self.request.resolver_match.app_name)
        return context

    def get_random_response(self, stage):
        return random.choice(self.responses[stage])

    
    def run_diagnosis(self, request):
        from core.chatbot_models_manager.src.models.NER import NERModel, MissingModelOrTokenizer
        from core.chatbot_models_manager.src.models.diagnoser import DiagnoserModel
        from django.apps import apps
        
        if(request.method != "POST"):
            return JsonResponse({"status": "error", "message": "Invalid request method"}, status=500)
        # sent_case = "i have been experiencing a lot of itching on my skin lately and it's driving me crazy i've also noticed some rashes on my skin and these weird nodal skin eruptions that seem to be spreading i'm not sure what's causing it but it's really starting to affect my daily life could you help me figure out what's going on"
        user_id = request.user.pk
        user_case = request.POST['case']
        try:
            app_config  = apps.get_app_config('chatbot')
            # symptoms = set(NERModel.Model.extract_symptoms(user_case))
            symptoms = set(NERModel.Model.extract_symptoms(user_case, app_config.ner_model, app_config.tokenizer))
            if len(symptoms) < 3:
                return JsonResponse({"status": "error", "message": "Too few symptoms extracted, please provide me with more information."}, status=500)
            diagnosis_result, normalized_symps = DiagnoserModel.Model.diagnose(symptoms, app_config.diagnoser_model)
            disease_id, diagnosis_id = self.log_diagnosis(diagnosis_result, normalized_symps, request.user.id)
            recomanded_doctor_id = self.suggest_doctor_depending_on_disease(user_id, disease_id)
            pritifications = self.get_purifications_to_disease(disease_id)
            request.session['booking_info'] = {
                'diagnosis_id': diagnosis_id,
                'recomanded_doctor_id': recomanded_doctor_id
            }

        except MissingModelOrTokenizer as e:
            print(str(e))
            return JsonResponse({"status": "error", "message": f"Symptom extraction failed: {str(e)}"}, status=500)
        except Exception as e:
            print(str(e))
            return JsonResponse({"status": "error", "message": f"Symptom extraction failed: {str(e)}"}, status=500)
        print("success!!!!")
        return JsonResponse({
            "status": "success",
            "result": {
                "symptoms": list(symptoms),
                "diagnosis": diagnosis_result,
                "purifications": pritifications,
                "recomanded_doctor": recomanded_doctor_id
            },
        })
    
    def get_purifications_to_disease(self, disease_id):
        disease = Diseases.objects.get(pk=disease_id)
        purifications = disease.purifications.all()
        #getting the descitions of the putiricaion
        return [p.description for p in purifications]
    
    def suggest_doctor_depending_on_disease(self, user_id, disease_id):
        custom_user = CustomUser.objects.get(id=user_id)  # Assuming you have the custom user object

        user_medical_record = UsersMeicalRecord.objects.get(user=custom_user)
        custom_user_city = user_medical_record.city

        doctors = DoctorsInformation.objects.filter(
            hospitals__city=custom_user_city
        )

        if not doctors.exists():
            return doctors_with_specialization
        else:
            doctors = DoctorsInformation.objects.all()

        disease = Diseases.objects.get(id=disease_id)
        doctors_with_specialization = doctors.filter(specialization__in=disease.specializations.all())
        if doctors_with_specialization.exists():
            #returning recomanded doctor id
            return doctors_with_specialization.order_by('-competence').first().id
        else:
            return None


    
    @transaction.atomic
    def log_diagnosis(self, diags, symps, subject_id):
        from django.contrib.auth import get_user_model
        from django.utils import timezone
        from core.chatbot.models import BotDiagnoses
        from core.healthcare.models import Diseases, Symptoms

        User = get_user_model()
        subject = User.objects.get(id=subject_id)
        symptoms_list = Symptoms.objects.filter(name__in = symps)
        diagnosis = Diseases.objects.get(name=diags)
        bot_diagnosis = BotDiagnoses.objects.create(
            diagnosis = diagnosis,
            diagnosis_date = timezone.now().date(),
            diagnosis_time = timezone.now().time(),
            subject = subject
        )
        bot_diagnosis.symptoms_group.set(symptoms_list)
        bot_diagnosis.save()
        return diagnosis.pk, bot_diagnosis.id

initChatbotView = ChatbotView()