from django.urls import reverse
from ..utls.helpers import user_belongs_to_group, redirect_to_match_site

class AdminPagesMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        admin_pages = [
            reverse('adminpage-user:index'),
            reverse('adminpage-doctor:index'),
            reverse('adminpage-admin:index')
        ]
        
        if request.user.is_authenticated and any(request.path.startswith(url) for url in admin_pages):
            if user_belongs_to_group(request.user, "User"):
                if not request.path.startswith(reverse('adminpage-user:index')) :
                    return redirect_to_match_site(request.user)
            elif user_belongs_to_group(request.user, "Doctor"):
                if not request.path.startswith(reverse('adminpage-doctor:index')) :
                    return redirect_to_match_site(request.user)
            elif request.user.is_superuser:
                if not request.path.startswith(reverse('adminpage-admin:index')):
                    return redirect_to_match_site(request.user)
        return self.get_response(request)
