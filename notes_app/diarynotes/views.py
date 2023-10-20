from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from . import serializers
from django.contrib.auth import authenticate, update_session_auth_hash
from django.core.exceptions import ObjectDoesNotExist
# Create your views here.

class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class UserLoginView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserLoginSerializer

    def post(self, request, *args, **kwargs):
        data = request.data
        email = data.get('email')
        password = data.get('password')
        user = None
        if '@' in email:
            try:
                user = User.objects.get(email=email)
            except ObjectDoesNotExist:
                return Response({'error': 'User does not exist!'}, status=status.HTTP_404_NOT_FOUND)

        if not user:
            user = authenticate(username=email, password=password)

        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)

        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class UserLogoutView(generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        #Get the user's token
        token, _ = Token.objects.get_or_create(user=request.user)

        #Expire the token
        token.delete()