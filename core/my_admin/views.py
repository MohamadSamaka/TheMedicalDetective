from django.views.generic import TemplateView
from django.http import HttpResponseNotAllowed
from django.contrib import messages
from .src.forms.user import UserMedicalInformation, UserGeneralInformation
from core.healthcare.models import UsersMedicalRecord
from core.authentication.src.services.email import EmailVerificationManager
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.core.cache import cache



class UserMedicalProfile(TemplateView):
    template_name = 'admin/user/pages/user_profile_page.html'
    def get_context_data(self, **kwargs):
        from core.my_admin.admin import my_user_site
        context = super().get_context_data(**kwargs)
        user = self.request.user
        init_user_medical_record = UsersMedicalRecord.objects.get(user=user)
        form = UserMedicalInformation(instance=init_user_medical_record)
        context['form'] = form
        context['available_apps'] = my_user_site.get_app_list(self.request)
        print("hmmm: ", self.request.POST)
        return context
    

    def post(self, request, *args, **kwargs):
        user = request.user
        init_user_medical_record = UsersMedicalRecord.objects.get(user=user)  # Retrieve your model instance
        form = UserMedicalInformation(request.POST, instance=init_user_medical_record)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your info changed successfully.')
        else:
            messages.error(request, 'Make sure of the form.')

        context = self.get_context_data()

        context['form'] = form

        return self.render_to_response(context)
    


class UserGeneralProfile(TemplateView, EmailVerificationManager):
    template_name = 'admin/user/pages/user_profile_page.html'
    subject = "Reset-Password"
    message = f"Your code to change email is: {EmailVerificationManager.code}"
    
    def get_context_data(self, **kwargs):
        from core.my_admin.admin import my_user_site
        context = super().get_context_data(**kwargs)
        user = self.request.user
        form = UserGeneralInformation(instance=user)
        context['form'] = form
        context['available_apps'] = my_user_site.get_app_list(self.request)
        return context
    

    def post(self, request, *args, **kwargs):
        from core.my_admin.admin import my_user_site
        user = request.user
        email = request.user.email
        print(request.POST)
        form = UserGeneralInformation(request.POST, instance=user)
        if form.is_valid():
            sent_email = request.POST.get('email')
            print("sent email: ", sent_email)
            if email != sent_email:
                print("wtf1")
                messages.error(request, 'You have to verify your new email to change it.')
                return HttpResponse('invalid code', status_code=404)
                # code = request.POST.get('code')
                # session_key = request.session.session_key
                # sent_inputs = {
                #     "email": sent_email,
                #     "first_name": request.POST.get('first_name'),
                #     "last_name": request.POST.get('last_name')
                # }
                # if not session_key:
                #     request.session.cycle_key()
                #     cache.set(session_key, sent_inputs, timeout=180)
                #     self.send_verification_code(request, sent_inputs)
                # print("wtf1: ", request.path_info)
                # return self.confirm_code(request)
            else:
                form.save()
                messages.success(request, 'Your info changed successfully.')
        else:
            messages.error(request, 'Make sure of the form.')
        print("wtf3: ", request.path_info)
        context = {
            'form': form,
            'available_apps': my_user_site.get_app_list(request)
        }

        return render(request, self.template_name, context)
    
    def email_exists(self, request):
        user_model = get_user_model()
        if request.method != 'POST':
            return HttpResponseNotAllowed(['POST'])
        try:
            email = request.POST.get('email')
            user_model.objects.get(email=email)
            return HttpResponse("This email is already taken", status=409)
        except user_model.DoesNotExist:
            return HttpResponse("email is valid")
        
    def send_code_to_new_email(self, request):
        from core.my_admin.admin import my_user_site
        user = request.user
        sent_email = request.POST.get('email')
        form = UserGeneralInformation(request.POST, instance=user)
        sent_inputs = {
                "email": sent_email,
                "first_name": request.POST.get('first_name'),
                "last_name": request.POST.get('last_name')
            }
        if form.is_valid():
            session_key = request.session.session_key
            if not session_key:
                request.session.cycle_key()
            print("the email is: ", sent_email)
            sent_inputs = {
                "email": sent_email,
                "first_name": request.POST.get('first_name'),
                "last_name": request.POST.get('last_name')
            }
            return self.send_verification_code(request, sent_inputs)
        context = {
            'form': form,
            'available_apps': my_user_site.get_app_list(request)
        }

        return render(request, self.template_name, context, status=404)
    
    def change_email(self, request):
        from core.my_admin.admin import my_user_site
        user = request.user
        session_key = request.session.session_key
        cached_user_info = cache.get(session_key)
        form = UserGeneralInformation(cached_user_info, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your info changed successfully.')
        else:
            messages.error(request, 'Something Went Wrong please make sure of the form.')
        context = {
            'form': form,
            'available_apps': my_user_site.get_app_list(request)
        }
        return render(request, self.template_name, context)
        
        

initUserGeneralProfile = UserGeneralProfile()
