from django.db import models
from django.contrib.auth.models import User
import os

def get_image_upload_path(instance, filename):
    """
    Define a custom upload path for images.
    Images will be organized by user ID to keep them separate.
    """
    return os.path.join('user_uploads', f'user_{instance.user.id}', filename)

class Image(models.Model):
    """
    Base model for storing original images uploaded by users.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='images')
    title = models.CharField(max_length=100, blank=True)
    file = models.ImageField(upload_to=get_image_upload_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s image: {self.title or 'Untitled'}"

    class Meta:
        ordering = ['-uploaded_at']

    def delete(self, *args, **kwargs):
        """
        Override delete method to also delete the image file
        when the model instance is deleted.
        """
        if self.file:
            if os.path.isfile(self.file.path):
                os.remove(self.file.path)

        # Call the parent class's delete method
        super().delete(*args, **kwargs)

class ImageEdit(models.Model):
    """
    Model to store edited versions of images with effects applied.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='image_edits')
    original_image = models.ImageField(upload_to=get_image_upload_path)
    edited_image = models.ImageField(upload_to=get_image_upload_path, blank=True)
    effect_applied = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s image edit ({self.id}) - {self.effect_applied}"

    class Meta:
        ordering = ['-created_at']

    def delete(self, *args, **kwargs):
        """
        Override delete method to also delete the image files
        when the model instance is deleted.
        """
        # Delete the image files from storage
        if self.original_image:
            if os.path.isfile(self.original_image.path):
                os.remove(self.original_image.path)

        if self.edited_image:
            if os.path.isfile(self.edited_image.path):
                os.remove(self.edited_image.path)

        # Call the parent class's delete method
        super().delete(*args, **kwargs)
