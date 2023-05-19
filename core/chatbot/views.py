from django.shortcuts import render

def index(request):
    parms = {'url_name': request.resolver_match.url_name}
    return render(request, 'client/pages/chatbot.html', parms)
