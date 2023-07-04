from django.urls import path
from .views import ChatbotView, initChatbotView

app_name = 'chatbot'

urlpatterns = [
    path('', ChatbotView.as_view(), name='index'),
    path('diagnose/', initChatbotView.run_diagnosis, name='diagnose'),
]
