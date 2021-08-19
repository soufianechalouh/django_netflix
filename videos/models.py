from django.db import models


class Video(models.Model):
    class VideoStateOptions(models.TextChoices):
        PUBLISHED = "PU", "Published"
        DRAFT = "DR", "Draft"
        UNLISTED = "UN", "Unlisted"
        PRIVATE = "PR", "Private"

    title = models.CharField(max_length=230)
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(blank=True, null=True)
    video_embed_id = models.CharField(max_length=255)
    active = models.BooleanField(default=True)
    state = models.CharField(max_length=2, choices=VideoStateOptions.choices, default=VideoStateOptions.DRAFT)

    @property
    def is_published(self):
        return self.active


class VideoPublishedProxy(Video):
    class Meta:
        proxy = True
        verbose_name = "Published Video"
        verbose_name_plural = "Published Videos"


class VideoAllProxy(Video):
    class Meta:
        proxy = True
        verbose_name = "Video"
        verbose_name_plural = "All Videos"
