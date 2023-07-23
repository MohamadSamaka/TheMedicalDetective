from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.core.cache import cache
from django.http import HttpResponseRedirect
import re
import shutil

def user_belongs_to_group(user, group_name):
    try:
        return user.groups.filter(name=group_name).exists()
    except Group.DoesNotExist:
        return False
    

def redirect_to_match_site(user):
    if user_belongs_to_group(user, "Doctor"):
        return HttpResponseRedirect(reverse('adminpage-doctor:index'))
    elif user_belongs_to_group(user, "User"):
        return HttpResponseRedirect(reverse('adminpage-user:index'))
    return HttpResponseRedirect(reverse('adminpage-admin:index'))

def delete_dir_with_contents_if_canceled(path, user_id):
    if cache.get(user_id).get('cancel_flag'):
        if path.is_dir():
            shutil.rmtree(path)
        cache.delete(user_id)
        return True
    return False

def delete_dir_with_contents(path):
    if path.is_dir():
        shutil.rmtree(path)
        return True
    return False


def is_valid_filename(value):
    pattern = r'^[a-zA-Z0-9_]+$' #only accepting characters, numbers and '_'
    return bool(re.match(pattern, value))


def validate_model_filename(value):
    if not is_valid_filename(value):
        raise ValidationError('Invalid filename, only charecters and numbers are allowed!')
    return True