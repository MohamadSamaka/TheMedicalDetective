from django.conf import settings
from django.urls import reverse
from django.core.mail import send_mail
from django.http import HttpResponseRedirect, HttpResponseBadRequest, HttpResponseServerError, HttpResponse
from django.core.cache import cache
from core.project import settings
from smtplib import SMTPException
from random import randint

class EmailVerificationManager():
    code = ''.join(str(randint(0, 9)) for _ in range(4))
    subject = None
    message = None


    def confirm_code(self, request):
        if request.method != 'POST':
            return HttpResponseRedirect(reverse('home'))
        if request.session.session_key:
            code = request.POST.get('code')
            session_key = request.session.session_key
            cached_user_info = cache.get(session_key)
            if not cached_user_info:
                return HttpResponse('Session key is missing or invalid', status=400)
            if cached_user_info.get('code') != code:
                return HttpResponse("Wrong code", status=401)
            if request.path_info == '/signup/confirm-code/':
                return self.create_user_with_medical_record(request)
            return HttpResponse('sucess')
            
        return HttpResponse('Something went wrong.', status=404)

    def send_verification_code(self, request, sent_inputs):
        print('time to send code!')
        minuets = int(settings.VERIFICATION_CODE_TIMEOUT)
        # receiver_email = "m.samaka2k@gmail.com"
        receiver_email = "mhmd_dragon1@hotmail.com"
        # receiver_email = sent_inputs.get('email')
        try:
            # send_mail(
            # self.subject,
            # self.message,
            # settings.EMAIL_HOST_USER,
            # [receiver_email],
            # fail_silently=False,
            # )
            pass
        except SMTPException as e:
            return HttpResponseServerError("Failed to send email: " + str(e))
        session_key = request.session.session_key
        if not session_key:
         return HttpResponseBadRequest("Session key not found.")
        sent_inputs.update({'code': self.code})
        cache.set(session_key, sent_inputs, minuets*60)
        print("generated code is: ", self.code)
