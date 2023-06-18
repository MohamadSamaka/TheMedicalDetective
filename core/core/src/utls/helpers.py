from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.urls import reverse

def user_belongs_to_group(user, group_name):
    try:
        return user.groups.filter(name=group_name).exists()
    except Group.DoesNotExist:
        return False
    

def redirect_to_user_or_doc_page(user):
    if user_belongs_to_group(user, "Doctor"):
        return HttpResponseRedirect(reverse('adminpage-doctor:index'))
    return HttpResponseRedirect(reverse('adminpage-admin:index'))