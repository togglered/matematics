from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy
from PIL import Image

from main.models import Task, Test


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(gettext_lazy('email address'), unique=True)
    teacher_flag = models.BooleanField(default=False)
    type = models.CharField(default='Ученик', max_length=50)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    gender = models.CharField(default='Мужской', max_length=50)
    favorites_tasks = models.ManyToManyField(Task, blank=True)
    favorites_tests = models.ManyToManyField(Test, blank=True)
    email_proof = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=1000, null=True)
    set_pass_link_created = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    objects = CustomUserManager()
    REQUIRED_FIELDS = []
    

    class Meta:
            db_table = 'user'


    def save(self, *args, **kwargs):
        if not self.first_name or not self.last_name:
            self.first_name = 'Имя'
            self.last_name = 'Фамилия'
        if self.teacher_flag:
            self.type = 'Учитель'
        else:
            self.type = 'Ученик'
        super().save(*args, **kwargs)

        if self.avatar:
            img = Image.open(self.avatar.path)
            width, height = img.size
            crop_size = min(width, height)
            left = (width - crop_size) / 2
            top = (height - crop_size) / 2
            right = (width + crop_size) / 2
            bottom = (height + crop_size) / 2
            img_cropped = img.crop((left, top, right, bottom))
            img_cropped.save(self.avatar.path)


    def __str__(self):
        return self.email