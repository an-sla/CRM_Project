from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .utils import assign_entries_to_users

@receiver(post_save, sender=User)
def assign_entries_on_user_creation(sender, instance, created, **kwargs):
    if created and not instance.is_superuser:
        assign_entries_to_users()
