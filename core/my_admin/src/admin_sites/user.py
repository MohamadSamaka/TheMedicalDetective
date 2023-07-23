
from core.core.admin import BaseAdminSite
from ...views import UserMedicalProfile, UserGeneralProfile, initUserGeneralProfile


class UserAdminSite(BaseAdminSite):
    site_header = 'User Dashboard'
    site_title = 'User Dashboard'
    index_title = 'User Dashboard'
    site_name = 'user-site'

    def has_permission(self, request):
        return request.user.is_authenticated
    

    
    def get_urls(self):
        from django.urls import path

        urls = super().get_urls()

        custom_urls = [
            path('medical-info', self.admin_view(UserMedicalProfile.as_view()), name='medical-info'),
            path('general-info', self.admin_view(UserGeneralProfile.as_view()), name='general-info'),
            path('email-exists', initUserGeneralProfile.email_exists, name='email-duplicate'),
            path('send-code', initUserGeneralProfile.send_code_to_new_email, name='send-code'),
            path('verify-code', initUserGeneralProfile.confirm_code, name='confirm_code'),
        ]

        return custom_urls + urls
