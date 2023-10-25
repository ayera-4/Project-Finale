from django.shortcuts import render
from django.contrib.auth.tokens import default_token_generator
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from . import serializers, models
from django.contrib.auth import authenticate, get_user_model, update_session_auth_hash
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.utils import timezone


class UserRegistrationView(generics.CreateAPIView):
    queryset = models.CustomUser.objects.all()
    serializer_class = serializers.UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class UserLoginView(generics.CreateAPIView):
    queryset = models.CustomUser.objects.all()
    serializer_class = serializers.UserLoginSerializer

    def post(self, request, *args, **kwargs):
        data = request.data
        email = data.get('email')
        password = data.get('password')
        user = None
        if '@' in str(email):
            try:
                user = models.CustomUser.objects.get(email=email)
            except ObjectDoesNotExist:
                return Response({'error': 'User does not exist!'}, status=status.HTTP_404_NOT_FOUND)

        if not user:
            user = authenticate(username=email, password=password)

        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'user_id': user.pk, 'email': user.email}, status=status.HTTP_200_OK)

        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class UserLogoutView(APIView):
    #permission_classes = [permissions.IsAuthenticated]
    def get(self, request, *args, **kwargs):
        #Get the user's token
        token, _ = Token.objects.get_or_create(user=request.user)
        if token:
            try:
                # Expire the token
                token.delete()
                return Response({'message': 'User Successfully logged out'}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({'error': 'No token detected'}, status=status.HTTP_404_NOT_FOUND)


class TokenExpirationView(APIView):
    def get(self, request):
        # Check if the user is authenticated and has a token
        if request.user.is_authenticated and hasattr(request.user, 'auth_token'):
            token = request.user.auth_token
            current_time = timezone.now()
            token_expires = token.created + token.settings.DEFAULT_EXPIRATION
            token_valid = current_time <= token_expires

            return Response({"valid": token_valid})
        else:
            return Response({"valid": False})


class PasswordResetRequestView(APIView):
    serializer_class = serializers.PasswordResetSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        user = get_user_model().objects.filter(email=email).first()
        if user:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_link = f"https://example.com/reset-password/{uid}/{token}/"
            subject = 'Password Reset Request'
            message = f'You can Reset your password by clicking this link: {reset_link}'
            from_email = 'noreply@example.com'
            recipient_list = [email]

            send_mail(subject, message, from_email, recipient_list)

        return Response({'message': 'Password reset email sent if the email exists'})


class PasswordResetConfirmView(APIView):
    serializer_class = serializers.PasswordResetConfirmSerializer

    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = get_user_model().objects.get(pk=uid)

            if default_token_generator.check_token(user, token):
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)

                new_password = serializer.validated_data['new_password']
                user.set_password(new_password)
                user.save()

                return Response({'message': 'Password reset successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
        except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
            return Response({'message': 'Invalid user or token'}, status=status.HTTP_400_BAD_REQUEST)

class NotesApiView(APIView):
    def get(self, request):
        api_urls = {
            'Create a category': 'category-add/',
            'Create a note': 'note-add/',
            'View list of notes': 'note-list/',
            'View a note': 'note-detail/<str:pk>/',
            'Update a note': 'note-update/<str:pk>/',
            'Delete a note': 'note-delete/<str:pk>/',
            'View latest notes': 'notes-latest/',
            'View unfinished notes': 'notes-unfinished/',
            'View overdue notes': 'notes-overdue/',
            'View sorted notes': 'notes-sorted/',
            'Share notes on email': 'notes-share/',
            'Set reminder for note': 'set-reminder/<str:note_id>/',
            'Export notes as PDF': 'export/pdf/',
            'Export notes as CSV': 'export/csv/',
            'Export notes as Excel': 'export/excel/',
        }
        return Response(api_urls)

class UserApiView(APIView):
    def get(self, request):
        api_urls = {
            'Register User': 'register/',
            'login User': 'login/',
            'logout User': 'logout/',
            'token expiration check': 'token-expiration/',
            'password reset': 'password-reset/',
            'confirm password reset': 'password-reset/confirm/<str:uidb64>/<str:token>/',

        }
        return Response(api_urls)