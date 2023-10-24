from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class CustomUser(AbstractUser):
    email = models.EmailField(verbose_name="Email", max_length=255, unique=True)
    first_name = models.CharField(verbose_name="First Name", max_length=255)
    last_name = models.CharField(verbose_name="Last Name", max_length=255)
    password = models.CharField(max_length=255)
    username = None

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

class Category(models.Model):
    name = models.CharField(max_length=255)

class Note(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    due_date = models.DateTimeField()
    unfinished = models.BooleanField()
    done = models.BooleanField()
    overdue = models.BooleanField()
    priority = models.CharField(max_length=20)
    created_time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
