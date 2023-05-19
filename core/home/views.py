from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    parms = {'url_name': request.resolver_match.url_name}
    return render(request, 'client/pages/home.html', parms)

def test(request, id):
    return HttpResponse(id)
