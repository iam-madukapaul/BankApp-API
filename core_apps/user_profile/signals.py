from typing import Any
from django.db.models.signals import post_save
from django.dispatch import receiver
from loguru import logger
from config.settings.base import AUTH_USER_MODEL
from core_apps.user_profile.models import Profile
from django.db.models import Model


@receiver(post_save, sender=AUTH_USER_MODEL)
def create_or_update_user_profile(
    sender: type[Model], instance: Model, created: bool, **kwargs: Any
) -> None:
    if created:
        Profile.objects.create(user=instance)
        logger.info(f"Profile created for {instance.first_name} {instance.last_name}")
    else:
        if hasattr(instance, "profile"):
            instance.profile.save()
