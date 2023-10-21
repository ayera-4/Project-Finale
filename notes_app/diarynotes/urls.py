from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.UserRegistrationView.as_view(), name="user-registration"),
    path('login/', views.UserLoginView.as_view(), name="user-login"),
    path('logout/', views.UserLogoutView.as_view(), name="user-logout"),
    path('password-reset/', views.PasswordResetRequestView.as_view(), name='password-reset'),
    path('password-reset/confirm/<str:uidb64>/<str:token>/', views.PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
]