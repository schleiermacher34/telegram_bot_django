# botapp/admin.py

from django.contrib import admin
from .models import UserData, VideoLink
from django.urls import path
from django.http import HttpResponse
from .utils import export_data_to_excel
from django.template.response import TemplateResponse

class CustomAdminSite(admin.AdminSite):
    site_header = 'Telegram Bot Admin'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('export-data/', self.admin_view(self.export_data), name='export-data'),
        ]
        return custom_urls + urls

    def export_data(self, request):
        if not request.user.is_staff:
            return HttpResponse('Unauthorized', status=401)
        return export_data_to_excel()

admin_site = CustomAdminSite(name='custom_admin')

class VideoLinkInline(admin.TabularInline):
    model = VideoLink
    extra = 0

@admin.register(UserData, site=admin_site)
class UserDataAdmin(admin.ModelAdmin):
    list_display = ('telegram_username', 'chat_id', 'serial_number')
    search_fields = ('telegram_username', 'serial_number')
    inlines = [VideoLinkInline]

    change_list_template = "admin/botapp/userdata_change_list.html"

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['export_url'] = 'export-data'
        return super().changelist_view(request, extra_context=extra_context)

@admin.register(VideoLink, site=admin_site)
class VideoLinkAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'video_link')
    search_fields = ('user__telegram_username', 'video_link')

    change_list_template = "admin/botapp/videolink_change_list.html"

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['export_url'] = 'export-data'
        return super().changelist_view(request, extra_context=extra_context)


