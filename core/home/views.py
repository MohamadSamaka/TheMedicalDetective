from django.views.generic import TemplateView
from core.healthcare.models import Hospitals
from django.conf import settings


# def index(request):
#     context = {'url_name': request.resolver_match.url_name}
#     return render(request, 'client/pages/home.html', context)

class HomeView(TemplateView):
    template_name = 'client/pages/home.html'  # Replace with your actual template name

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hospitals = Hospitals.objects.all()  # Fetch data from your model as needed
        context['url_name'] = self.request.resolver_match.url_name
        context['MEDIA_URL'] =  settings.MEDIA_URL
        context['hospitals'] = hospitals
        return context