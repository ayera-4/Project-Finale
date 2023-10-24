from django.urls import path
from . import user_views

urlpatterns = [
    path('register/', user_views.UserRegistrationView.as_view(), name="user-registration"),
    path('login/', user_views.UserLoginView.as_view(), name="user-login"),
    path('logout/', user_views.UserLogoutView.as_view(), name="user-logout"),
    path('token-expiration/', user_views.TokenExpirationView.as_view(), name='token-expiration'),
    path('password-reset/', user_views.PasswordResetRequestView.as_view(), name='password-reset'),
    path('password-reset/confirm/<str:uidb64>/<str:token>/', user_views.PasswordResetConfirmView.as_view(), name='confirm-password-reset'),
    path('user-view/', user_views.UserApiView.as_view(), name="user-view"),
    path('notes-view/', user_views.NotesApiView.as_view(), name="notes-view"),
]