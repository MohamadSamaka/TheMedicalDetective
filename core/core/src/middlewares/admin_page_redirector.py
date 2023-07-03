from django.shortcuts import redirect
from django.urls import reverse
from ..utls.helpers import user_belongs_to_group, redirect_to_user_or_doc_page

class AdminPagesMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if user_belongs_to_group(request.user, "User"):
                    return self.get_response(request)
            if user_belongs_to_group(request.user, "Doctor"):
                if request.path.startswith(reverse('adminpage-admin:index')) :
                    return redirect_to_user_or_doc_page(request.user)
            else:
                if request.path.startswith(reverse('adminpage-doctor:index')):
                    return redirect_to_user_or_doc_page(request.user)
        return self.get_response(request)
