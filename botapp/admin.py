from django.contrib import admin
from .models import UserData, VideoLink

class VideoLinkInline(admin.TabularInline):
    model = VideoLink
    extra = 0

@admin.register(UserData)
class UserDataAdmin(admin.ModelAdmin):
    list_display = ('telegram_username', 'chat_id', 'serial_number')
    search_fields = ('telegram_username', 'serial_number')
    inlines = [VideoLinkInline]

@admin.register(VideoLink)
class VideoLinkAdmin(admin.ModelAdmin):
    list_display = ('user', 'video_link')
    search_fields = ('user__telegram_username', 'video_link')

