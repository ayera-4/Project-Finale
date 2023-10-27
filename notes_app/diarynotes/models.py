from django.db import models
from django.contrib.auth.models import AbstractUser
from model_utils import Choices

# Create your models here.
class CustomUser(AbstractUser):
    username = models.CharField(verbose_name="Username", max_length=255, null=True, blank=True, unique=True)
    email = models.EmailField(verbose_name="Email", max_length=255, unique=True)
    first_name = models.CharField(verbose_name="First Name", max_length=255)
    last_name = models.CharField(verbose_name="Last Name", max_length=255)
    password = models.CharField(max_length=255)

    #USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["email", "first_name", "last_name"]

class Note(models.Model):
    CATEGORY = Choices("Operations", "Finance", "Marketing", "People")
    PRIORITY = Choices("High", "Moderate", "Low")
    title = models.CharField(max_length=255)
    content = models.TextField()
    due_date = models.DateTimeField(blank=True, null=True)
    done = models.BooleanField()
    priority = models.CharField(max_length=20, choices=PRIORITY)
    category = models.CharField(max_length=255, choices=CATEGORY)
    created_time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

