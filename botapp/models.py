# botapp/models.py

from django.db import models

class UserData(models.Model):
    telegram_username = models.CharField(max_length=150, null=True, blank=True)
    chat_id = models.BigIntegerField(unique=True)
    serial_number = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"{self.telegram_username} ({self.chat_id})"

class VideoLink(models.Model):
    user = models.ForeignKey(UserData, on_delete=models.CASCADE, related_name='video_links')
    video_link = models.URLField()

    class Meta:
        unique_together = ('user', 'video_link')

    def __str__(self):
        return f"VideoLink for {self.user}: {self.video_link}"
