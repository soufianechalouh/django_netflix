from django.contrib import admin

from .models import VideoAllProxy, VideoPublishedProxy


class VideoAllProxyAdmin(admin.ModelAdmin):
    list_display = ["title", "video_embed_id"]
    search_fields = ["title"]

    class Meta:
        model = VideoAllProxy


class VideoPublishedProxyAdmin(admin.ModelAdmin):
    list_display = ["title", "video_embed_id"]
    search_fields = ["title"]

    class Meta:
        model = VideoPublishedProxy

    def get_queryset(self, request):
        return VideoPublishedProxy.objects.filter(active=True)


admin.site.register(VideoAllProxy, VideoAllProxyAdmin)
admin.site.register(VideoPublishedProxy, VideoPublishedProxyAdmin)
