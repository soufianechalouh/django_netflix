from django.db import models


class Video(models.Model):
    title = models.CharField(max_length=230)
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(blank=True, null=True)
    video_embed_id = models.CharField(max_length=255)


class VideoProxy(Video):
    class Meta:
        proxy = True
        verbose_name = "Published Video"
        verbose_name_plural = "Published Videos"
