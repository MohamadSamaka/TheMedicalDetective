from django.views.generic import TemplateView
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.http import HttpResponseNotAllowed, HttpResponseBadRequest
from django.urls import reverse
from django.shortcuts import render
from django.core.cache import cache
from ..services.email import EmailVerificationManager
from core.core.models import City, CustomUser
from ..forms.register import SignUpForm



class MyRegistrationView(TemplateView, EmailVerificationManager):
    template_name = 'authentication/pages/sign-up.html'
    subject = "Email Confirmation"
    message = f"Welcome to The Medical Detective, we are glad to have you with us. Please verify your email address using the code below to complete your registration! your code is: {EmailVerificationManager.code}"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cities'] = City.objects.all().values('id', 'name')
        context['gender'] = [{'id': 0, 'name': 'Male'}, {'id': 1, 'name': 'Female'}]
        return context
        

    def get(self, request):
        if request.user.is_authenticated and request.user.is_superuser:
            return HttpResponseRedirect(reverse('admin:index'))
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('home'))
        context = self.get_context_data()
        return render(request, 'authentication/pages/sign-up.html', context)
    

    def register_user(self, request):
        if request.method != 'POST':
            return HttpResponseRedirect(reverse('home'))
        sent_inputs = request.POST
        session_key = request.session.session_key
        form_data = {
            'email': sent_inputs.get('email'),
            'first_name': sent_inputs.get('fname'),
            'last_name': sent_inputs.get('lname'),
            'phone_num': sent_inputs.get('phone-num'),
            'password': sent_inputs.get('pass'),
            'height': sent_inputs.get('height'),
            'weight': sent_inputs.get('weight'),
            'city':  City(int(sent_inputs.get('city'))),
            'blood_type': int(sent_inputs.get('blood-type')),
            'bdate': sent_inputs.get('bdate'),
            'gender': sent_inputs.get('gender'),
        }
        form = SignUpForm(form_data)
        if not form.is_valid():
            # return the errors in the form
            return HttpResponse(form.errors.as_json(), 400)
        if not session_key:
            request.session.cycle_key()
            session_key = request.session.session_key

        # processed_inputs = {}
        # for key in validationRules.keys():
        #     processed_inputs[key] = sent_inputs[key]
        #     # request.session[key] = sent_inputs[key]



        # cache.set(session_key, sent_inputs, timeout=180)
        self.send_verification_code(request, form_data)
        print("code sent!")
        return JsonResponse({'success': True})
    
    
    # @transaction.atomic
    def create_user_with_medical_record(self, request):
    # def create_user_with_medical_record(self, request):
        session_key = request.session.session_key
        cached_user_info = cache.get(session_key)
        form = SignUpForm(cached_user_info)
        if form.is_valid():
            return form.save()
        else:
            return HttpResponse(form.errors.as_json(), 400)    


    def email_exists(self, request):
        if request.method != 'POST':
            return HttpResponseRedirect(reverse('home'))
        try:
            email = request.POST.get('email')
            CustomUser.objects.get(email=email)
            return HttpResponse("This email is already taken", status=409)
        except CustomUser.DoesNotExist:
            return HttpResponse("email is valid") 