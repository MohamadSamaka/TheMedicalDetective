from django.apps import AppConfig
import sys


class ChatbotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.chatbot'

    def ready(self):
        if 'runserver' in sys.argv:
            from core.chatbot_models_manager.src.models.diagnoser import DiagnoserModel
            from core.chatbot_models_manager.src.models.NER import NERModel
            # self.ner_model, self.tokenizer = NERModel.Model.load_model(), NERModel.Tokenizer.load_tokenizer()
            # self.diagnoser_model = DiagnoserModel.Model.load_model()
            self.ner_model, self.tokenizer = None, None
            self.diagnoser_model = None