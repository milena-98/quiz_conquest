from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class User(AbstractUser):
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username


class Profile(models.Model):
    AVATAR_CHOICES = [
        ('knight-1', 'knight-1'),
        ('knight-2', 'knight-2'),
        ('knight-3', 'knight-3'),
        ('knight-4', 'knight-4'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    nickname = models.CharField(max_length=30, unique=True)
    avatar_key = models.CharField(max_length=30, choices=AVATAR_CHOICES, default='knight-1')

    def __str__(self):
        return self.nickname


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance, defaults={'nickname': instance.username})
