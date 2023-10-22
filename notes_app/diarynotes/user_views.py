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
        if '@' in email:
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
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, *args, **kwargs):
        #Get the user's token
        token, _ = Token.objects.get_or_create(user=request.user)
        #token, _ = Token.objects.get_or_create(user=request.data)
        try:
            token.delete()
            return Response({'message': 'Successfully logged out.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        """
        if token:
            try:
                # Expire the token
                token.delete()
                return Response({'message': 'User Successfully logged out'}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({'error': 'No token detected'}, status=status.HTTP_404_NOT_FOUND)
        """


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