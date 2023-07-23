from django.conf import settings
from django.conf.urls.static import static
from .views import custom_serve

urlpatterns = [
    
] + static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT,
    show_indexes=True,
    view=custom_serve
)