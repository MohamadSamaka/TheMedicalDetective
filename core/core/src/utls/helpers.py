from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.core.cache import cache
import shutil

def user_belongs_to_group(user, group_name):
    try:
        return user.groups.filter(name=group_name).exists()
    except Group.DoesNotExist:
        return False
    

def redirect_to_user_or_doc_page(user):
    if user_belongs_to_group(user, "Doctor"):
        return HttpResponseRedirect(reverse('adminpage-doctor:index'))
    return HttpResponseRedirect(reverse('adminpage-admin:index'))

def delete_dir_with_contents_if_canceled(path, user_id):
    if cache.get(user_id).get('cancel_flag'):
        if path.is_dir():
            shutil.rmtree(path)
        cache.delete(user_id)
        return True
    return False
    