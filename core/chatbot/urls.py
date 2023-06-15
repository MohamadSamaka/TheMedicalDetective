from django.urls import path
from .views import ChatbotView, initChatbotView

urlpatterns = [
    path('', ChatbotView.as_view(), name='chatbot'),
    path('diagnose/', initChatbotView.run_diagnosis, name='diagnose'),
]
