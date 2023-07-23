from django.shortcuts import render
from django.conf import settings

def index(request):
    context = {
        'url_name': request.resolver_match.url_name,
        'MEDIA_URL': settings.MEDIA_URL,
    }
    return render(request, 'client/pages/clinics.html', context)
