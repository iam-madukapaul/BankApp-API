import base64
from uuid import UUID
import cloudinary.uploader
from celery import shared_task
from django.apps import apps
from django.core.files.storage import default_storage
from loguru import logger


@shared_task(bind=True, name="upload_photos_to_cloudinary", max_retries=3)
def upload_photos_to_cloudinary(self, profile_id: UUID, photos: dict) -> None:
    try:
        profile_model = apps.get_model("user_profile", "Profile")
        profile = profile_model.objects.get(id=profile_id)

        for field_name, photo_data in photos.items():
            if photo_data["type"] == "base64":
                image_content = base64.b64decode(photo_data["data"])
                response = cloudinary.uploader.upload(image_content)
            else:
                file_path = photo_data["data"]
                if default_storage.exists(file_path):
                    with default_storage.open(file_path, "rb") as image_file:
                        response = cloudinary.uploader.upload(image_file)
                    default_storage.delete(file_path)
                else:
                    logger.warning(f"File at path {file_path} not found.")
                    continue  # Skip to the next photo

            setattr(profile, field_name, response["public_id"])
            setattr(profile, f"{field_name}_url", response["url"])

        profile.save()
        logger.info(f"Photos for {profile.user.email} uploaded successfully.")

    except Exception as e:
        logger.error(f"Failed to upload photos for profile {profile_id}: {str(e)}")

        # Cleanup temp files if task fails
        for photo_data in photos.values():
            if photo_data["type"] == "file":
                file_path = photo_data.get("path")
                if file_path and default_storage.exists(file_path):
                    default_storage.delete(file_path)

        # Retry the task up to 3 times
        raise self.retry(exc=e, countdown=60)
