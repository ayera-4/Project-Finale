from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Note

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password']
        extra_kwargs = {'password': {'write_only': True}}

class UserLoginSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True)
    new_password_confirmation = serializers.CharField(write_only=True)

class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ['title', 'content', 'due_date', 'priority']