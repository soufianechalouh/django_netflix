from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.db.models.signals import pre_save
from django.db.models import Avg, Max, Min, Q
from django.utils import timezone

from django_netflix.db.models import PublishStateOptions
from django_netflix.db.receivers import publish_state_pre_save, unique_slugify_pre_save

from categories.models import Category
from ratings.models import Rating
from tags.models import TaggedItem
from videos.models import Video


class PlaylistQueryset(models.QuerySet):
    def published(self):
        return self.filter(state=PublishStateOptions.PUBLISHED, publish_timestamp__lte=timezone.now())

    def search(self, query=None):
        if query is None:
            return self.none()
        return self.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(category__title__icontains=query) |
            Q(category__slug__icontains=query) |
            Q(tags__tag__icontains=query)
        ).distinct()

    def movie_or_show(self):
        return self.filter(
            Q(type=Playlist.PlaylistTypeChoices.MOVIE) |
            Q(type=Playlist.PlaylistTypeChoices.TV_SHOW)
        )


class PlaylistManager(models.Manager):
    def get_queryset(self):
        return PlaylistQueryset(self.model, using=self._db)

    def published(self):
        return self.get_queryset().published()

    def featured_playlists(self):
        return self.get_queryset().filter(type=Playlist.PlaylistTypeChoices.PLAYLIST)


class Playlist(models.Model):
    class PlaylistTypeChoices(models.TextChoices):
        MOVIE = "MOV", "Movie"
        TV_SHOW = "TVS", "TV Show"
        SEASON = "SEA", "Season"
        PLAYLIST = "PLY", "Playlist"

    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL)
    related = models.ManyToManyField("self", blank=True, related_name="related", through="PlaylistRelated")
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
    tags = GenericRelation(TaggedItem, related_query_name="playlist")
    ratings = GenericRelation(Rating, related_query_name="playlist")

    objects = PlaylistManager()

    def __str__(self):
        return self.title

    def get_related_items(self):
        return self.playlistrelated_set.all()

    def get_absolute_url(self):
        if self.is_movie:
            return f"/movies/{self.slug}/"
        if self.is_show:
            return f"/shows/{self.slug}/"
        if self.parent is not None and self.is_season:
            return f"/shows/{self.parent.slug}/seasons/{self.slug}/"
        return f"/playlists/{self.slug}/"

    @property
    def is_movie(self):
        return self.type == self.PlaylistTypeChoices.MOVIE

    @property
    def is_show(self):
        return self.type == self.PlaylistTypeChoices.TV_SHOW

    @property
    def is_season(self):
        return self.type == self.PlaylistTypeChoices.SEASON

    def get_rating_avg(self):
        return Playlist.objects.filter(id=self.pk).aggregate(Avg("ratings__value"))

    def get_rating_spread(self):
        return Playlist.objects.filter(id=self.pk).aggregate(max=Max("ratings_value"), min=Min("ratings_value"))

    def get_short_display(self):
        return ""

    @property
    def is_published(self):
        return self.active

    def get_video_id(self):
        """Get main video id to render movie for user"""
        return self.video.get_video_id()

    def get_clips(self):
        """Get clips to render clips for user"""
        return self.playlistitem_set.all().published()


class MovieProxyManager(PlaylistManager):
    def all(self):
        return self.get_queryset().filter(type=Playlist.PlaylistTypeChoices.MOVIE)


class MovieProxy(Playlist):

    objects = MovieProxyManager()

    def get_movie_id(self):
        return self.get_video_id()

    class Meta:
        verbose_name = "Movie"
        verbose_name_plural = "Movies"
        proxy = True

    def save(self, *args, **kwargs):
        self.type = Playlist.PlaylistTypeChoices.MOVIE
        super().save(*args, **kwargs)


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

    @property
    def seasons(self):
        return self.playlist_set.published()

    def get_short_display(self):
        return f"{self.seasons.count()} Seasons"


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

    def get_season_trailer(self):
        """Get movie id to render movie for user"""
        return self.video.get_video_id()

    def get_episodes(self):
        """Get episodes to render clips for user"""
        return self.get_clips()


class PlaylistItemQueryset(models.QuerySet):
    def published(self):
        return self.filter(video__state=PublishStateOptions.PUBLISHED,
                           video__publish_timestamp__lte=timezone.now(),
                           playlist__state=PublishStateOptions.PUBLISHED,
                           playlist__publish_timestamp__lte=timezone.now()
                           )


class PlaylistItemManager(models.Manager):
    def get_queryset(self):
        return PlaylistItemQueryset(self.model, using=self._db)

    def published(self):
        return self.get_queryset().published()


class PlaylistItem(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    order = models.IntegerField(default=1)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = PlaylistItemManager()

    class Meta:
        ordering = ["order", "-timestamp"]


def pr_limit_choices_to():
    return Q(type=Playlist.PlaylistTypeChoices.MOVIE) | Q(type=Playlist.PlaylistTypeChoices.TV_SHOW)


class PlaylistRelated(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    related = models.ForeignKey(Playlist, on_delete=models.CASCADE,
                                related_name="related_item",
                                limit_choices_to=pr_limit_choices_to)
    order = models.IntegerField(default=1)
    timestamp = models.DateTimeField(auto_now_add=True)


pre_save.connect(publish_state_pre_save, sender=TVShowProxy)
pre_save.connect(unique_slugify_pre_save, sender=TVShowProxy)

pre_save.connect(publish_state_pre_save, sender=TVShowSeasonProxy)
pre_save.connect(unique_slugify_pre_save, sender=TVShowSeasonProxy)

pre_save.connect(publish_state_pre_save, sender=MovieProxy)
pre_save.connect(unique_slugify_pre_save, sender=MovieProxy)

pre_save.connect(publish_state_pre_save, sender=Playlist)
pre_save.connect(unique_slugify_pre_save, sender=Playlist)

