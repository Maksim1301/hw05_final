from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordChangeView,
    PasswordResetView,
)
from django.urls import path

from users.views import SignUp

app_name = 'users'

urlpatterns = [
    # Выход
    path('logout/',
         LogoutView.as_view(template_name='users/logged_out.html'),
         name='logout'),
    # Регистрация
    path('signup/',
         SignUp.as_view(template_name='users/signup.html'),
         name='signup'),
    # Авторизация
    path('login/',
         LoginView.as_view(template_name='users/login.html'),
         name='login'),
    # Восстановление пароля
    path('password_reset/',
         PasswordResetView.as_view
         (template_name='users/password_reset_form.html'),
         name='password_reset'),
    # Смена пароля
    path('password_change/',
         PasswordChangeView.as_view
         (template_name='users/password_reset_confirm.html'),
         name='password_change'),
]
