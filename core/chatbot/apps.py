from django.apps import AppConfig
import sys


class ChatbotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.chatbot'

    def ready(self):
        if 'runserver' in sys.argv:
            from core.chatbot_models_manager.src.models.diagnoser import DiagnoserModel
            from core.chatbot_models_manager.src.models.NER import NERModel
            from core.chatbot.models import ChatbotSettings
            try:
                model = ChatbotSettings.objects.first()
                diagnoser_model_name = model.used_diagnoser_model.model_name
                ner_model_name = model.used_ner_model.model_name
                self.ner_model, self.tokenizer = NERModel.Model.load_model(ner_model_name), NERModel.Tokenizer.load_tokenizer(ner_model_name)
                self.diagnoser_model = DiagnoserModel.Model.load_model(diagnoser_model_name)
            except:
                print("failed to load models")
                self.ner_model, self.tokenizer = None, None
                self.diagnoser_model = None