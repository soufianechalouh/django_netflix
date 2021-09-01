from django.db import models
from django.db.models.signals import pre_save
from django.utils import timezone

from django_netflix.db.models import PublishStateOptions
from django_netflix.db.receivers import publish_state_pre_save, slugify_pre_save


class VideoQueryset(models.QuerySet):
    def published(self):
        return self.filter(state=PublishStateOptions.PUBLISHED, publish_timestamp__lte=timezone.now())


class VideoManager(models.Manager):
    def get_queryset(self):
        return VideoQueryset(self.model, using=self._db)

    def published(self):
        return self.get_queryset().published()


class Video(models.Model):
    title = models.CharField(max_length=230)
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(blank=True, null=True)
    video_embed_id = models.CharField(max_length=255, unique=True)
    active = models.BooleanField(default=True)
    state = models.CharField(max_length=2, choices=PublishStateOptions.choices, default=PublishStateOptions.DRAFT)
    publish_timestamp = models.DateTimeField(auto_now=False, auto_now_add=False, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = VideoManager()

    def get_video_id(self):
        if not self.is_published:
            return None
        return self.video_embed_id

    @property
    def is_published(self):
        if self.active is False:
            return False
        state = self.state
        if state != PublishStateOptions.PUBLISHED:
            return False
        if (pub_timestamp := self.publish_timestamp) is None:
            return False
        now = timezone.now()
        return pub_timestamp <= now

    def get_playlists_ids(self):
        return list(self.playlist_featured.all().values_list("id", flat=True))


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


pre_save.connect(publish_state_pre_save, sender=Video)
pre_save.connect(slugify_pre_save, sender=Video)
