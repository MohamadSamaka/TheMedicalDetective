# from core.my_admin.admin import my_admin_site
from django.contrib.auth.models import Group
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib.admin import AdminSite
from core.authentication.src.views.login import MyLoginView
from core.core.src.utls.helpers import user_belongs_to_group
from .models import City

class BaseAdminSite(AdminSite):
    login_template = 'authentication/pages/log-in.html'

    def index(self, request, extra_context=None):
        if request.user.is_authenticated:
            if user_belongs_to_group(request.user, "Doctor"):
                if not request.path.startswith(reverse('adminpage-doctor:index')):
                    return HttpResponseRedirect(reverse('adminpage-doctor:index'))
            else:
                if not request.path.startswith(reverse('adminpage-admin:index')):
                    return HttpResponseRedirect(reverse('adminpage-admin:index'))

        return super().index(request, extra_context)


from core.my_admin.admin import my_admin_site
my_admin_site.register(City)