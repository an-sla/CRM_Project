from django.contrib.auth.models import User
from .models import CustomerData


def assign_entries_to_users():
    entries_per_user = 20
    entries = CustomerData.objects.filter(user=None).order_by('-id')[:entries_per_user * 2]
    users = User.objects.filter(is_superuser=False)

    for i, entry in enumerate(entries):
        user = users[i // entries_per_user % len(users)]
        entry.user = user
        entry.save()


def remove_user_assignments():
    entries = CustomerData.objects.all()

    for entry in entries:
        entry.user = None
        entry.save()
