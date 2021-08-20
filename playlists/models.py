from django.db import models
from django.db.models.signals import pre_save
from django.utils import timezone

from categories.models import Category
from django_netflix.db.models import PublishStateOptions
from django_netflix.db.receivers import publish_state_pre_save, slugify_pre_save
from videos.models import Video


class PlaylistQueryset(models.QuerySet):
    def published(self):
        return self.filter(state=PublishStateOptions.PUBLISHED, publish_timestamp__lte=timezone.now())


class PlaylistManager(models.Manager):
    def get_queryset(self):
        return PlaylistQueryset(self.model, using=self._db)

    def published(self):
        return self.get_queryset().published()


class Playlist(models.Model):
    class PlaylistTypeChoices(models.TextChoices):
        MOVIE = "MOV", "Movie"
        TV_SHOW = "TVS", "TV Show"
        SEASON = "SEA", "Season"
        PLAYLIST = "PLY", "Playlist"

    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL)
    category = models.ForeignKey(Category, related_name="playlists", blank=True, null=True, on_delete=models.SET_NULL)
    order = models.IntegerField(default=1)
    title = models.CharField(max_length=230)
    type = models.CharField(max_length=3, choices=PlaylistTypeChoices.choices, default=PlaylistTypeChoices.PLAYLIST)
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(blank=True, null=True)
    video = models.ForeignKey(Video, related_name="playlist_featured", blank=True, null=True, on_delete=models.SET_NULL)
    videos = models.ManyToManyField(Video, related_name="playlist_item", blank=True, through="PlaylistItem")
    active = models.BooleanField(default=True)
    state = models.CharField(max_length=2, choices=PublishStateOptions.choices, default=PublishStateOptions.DRAFT)
    publish_timestamp = models.DateTimeField(auto_now=False, auto_now_add=False, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = PlaylistManager()

    def __str__(self):
        return self.title

    @property
    def is_published(self):
        return self.active


pre_save.connect(publish_state_pre_save, sender=Playlist)
pre_save.connect(slugify_pre_save, sender=Playlist)


class TVShowProxyManager(PlaylistManager):
    def all(self):
        return self.get_queryset().filter(parent__isnull=True, type=Playlist.PlaylistTypeChoices.TV_SHOW)


class TVShowProxy(Playlist):

    objects = TVShowProxyManager()

    class Meta:
        verbose_name = "TV Show"
        verbose_name_plural = "TV Shows"
        proxy = True

    def save(self, *args, **kwargs):
        self.type = Playlist.PlaylistTypeChoices.TV_SHOW
        super().save(*args, **kwargs)


class MovieProxyManager(PlaylistManager):
    def all(self):
        return self.get_queryset().filter(parent__isnull=False, type=Playlist.PlaylistTypeChoices.MOVIE)


class MovieProxy(Playlist):

    objects = MovieProxyManager()

    class Meta:
        verbose_name = "Movie"
        verbose_name_plural = "Movies"
        proxy = True

    def save(self, *args, **kwargs):
        self.type = Playlist.PlaylistTypeChoices.MOVIE
        super().save(*args, **kwargs)


class TVShowSeasonManager(PlaylistManager):
    def all(self):
        return self.get_queryset().filter(parent__isnull=False, type=Playlist.PlaylistTypeChoices.SEASON)


class TVShowSeasonProxy(Playlist):

    objects = TVShowSeasonManager()

    class Meta:
        verbose_name = "Season"
        verbose_name_plural = "Seasons"
        proxy = True

    def save(self, *args, **kwargs):
        self.type = Playlist.PlaylistTypeChoices.SEASON
        super().save(*args, **kwargs)


class PlaylistItem(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    order = models.IntegerField(default=1)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "-timestamp"]
