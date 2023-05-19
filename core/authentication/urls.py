from django.urls import path
from .src.views.logout import LogoutView
from .src.views.register import MyRegistrationView
from .src.views.login import MyLoginView

initMyRegistrationView = MyRegistrationView()
initMyLoginView = MyLoginView()


urlpatterns = [
    path('login/', MyLoginView.as_view(), name='login'),
    path('login/send-restore-code/', initMyLoginView.reset_password, name='send-restore-code'),
    path('login/confirm-code/', initMyLoginView.confirm_code, name='send-restore-code'),
    path('login/reset-password/', initMyLoginView.change_password, name='reset-password'),
    path('signup/', MyRegistrationView.as_view(), name="signup"),
    path('signup/store-user/', initMyRegistrationView.register_user, name="store-user"),
    path('signup/confirm-code/', initMyRegistrationView.confirm_code, name="confirm-code"),
    path('signup/email-exists/', initMyRegistrationView.email_exists, name="check-email-exist"),
    path('logout/', LogoutView.as_view(), name="logout"),
]
