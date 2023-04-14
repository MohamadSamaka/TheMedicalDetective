from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return render(request, 'client/pages/home.html')

def test(request, id):
    return HttpResponse(id)
