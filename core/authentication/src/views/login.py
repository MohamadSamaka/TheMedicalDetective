from django.views.generic import TemplateView
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.http import HttpResponseNotAllowed, HttpResponseBadRequest
from django.urls import reverse
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LoginView
from django.core.cache import cache
from ..services.email import EmailVerificationManager
from core.my_admin.models import CustomUser
from core.core.src.utls.helpers import redirect_to_user_or_doc_page





class MyLoginView(LoginView, EmailVerificationManager):
    template_name = 'authentication/pages/log-in.html'
    subject = "Reset-Password"
    message = f"Your reset password is: {EmailVerificationManager.code}"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_superuser or request.user.is_staff:
            return redirect_to_user_or_doc_page(request.user)
        elif request.user.is_authenticated:
            return HttpResponseRedirect(reverse('home'))
        # else:
        return super().get(request, *args, **kwargs)
            # return HttpResponseRedirect(reverse('home'))

    def form_valid(self, form):
        # Custom form submission handling code here
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None and user.is_active:
            login(self.request, user)
            if not user.is_superuser and not user.is_staff and not user.is_admin:
                return HttpResponseRedirect(reverse('home'))
            return redirect_to_user_or_doc_page(user)
        else:
            # Authentication failed
            return self.form_invalid(form)
        
    def form_invalid(self, form):
        return JsonResponse({'success': False, 'errors': form.errors.as_json()}, status=400)
    
    def reset_password(self, request):
        if request.method != 'POST':
            return HttpResponseRedirect(reverse('home'))
        session_key = request.session.session_key
        email = request.POST.get('email')
        # email = "mhmd_dragon1@hotmail.com"
        if not session_key:
            request.session.cycle_key()
        cache.set(session_key, {'email': email}, timeout=180)
        sent_inputs = {'email': email}
        self.send_verification_code(request, sent_inputs)
        print("code sent!")
        return JsonResponse({'success': True})
    
    def change_password(self, request):
        if request.method != 'POST':
            return HttpResponseRedirect(reverse('home'))
        new_pass = request.POST.get('new-pass')
        session_key = request.session.session_key
        if not session_key:
            return HttpResponseBadRequest("Session key not found.")
        cached_email = cache.get(session_key).get('email')
        print("new pass: ", new_pass)
        user = CustomUser.objects.get(email=cached_email)
        user.set_password(new_pass)
        user.save()
        return HttpResponse("password changed successfully")