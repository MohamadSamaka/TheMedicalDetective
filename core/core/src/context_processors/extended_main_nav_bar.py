from django.urls import reverse

def customize_main_sidebar(request):
    context = {}
    if hasattr(request, 'user'):
        context['is_user_admin_page'] = request.path.startswith(reverse('adminpage-user:index'))
    return context
