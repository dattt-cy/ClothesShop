from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Account, UserProfile


@receiver(post_save, sender=Account)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Only create if not exists (safety for rare race conditions)
        UserProfile.objects.get_or_create(
            user=instance,
            defaults={'profile_picture': 'default/default-user.png'}
        )


@receiver(post_save, sender=Account)
def save_user_profile(sender, instance, **kwargs):
    # Ensure a profile always exists (covers migrated legacy users without profile)
    UserProfile.objects.get_or_create(
        user=instance,
        defaults={'profile_picture': 'default/default-user.png'}
    )
