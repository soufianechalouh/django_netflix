from django.test import TestCase
from django.utils import timezone
from django.utils.text import slugify

from django_netflix.db.models import PublishStateOptions
from videos.models import Video
from .models import Playlist


class PlaylistModelTestCase(TestCase):

    def create_show_with_seasons(self):
        the_office = Playlist.objects.create(title="The Office Series")
        season_1 = Playlist.objects.create(title="The Office Series season 1", parent=the_office, order=1)
        season_2 = Playlist.objects.create(title="The Office Series season 2", parent=the_office, order=2)
        season_3 = Playlist.objects.create(title="The Office Series season 3", parent=the_office, order=3)
        self.show = the_office

    def create_videos(self):
        video_a = Video.objects.create(title='test title', video_embed_id="abc")
        video_b = Video.objects.create(title='test video b', video_embed_id="def")
        video_c = Video.objects.create(title='test video c', video_embed_id="ghi")
        self.video_a = video_a
        self.video_b = video_b
        self.video_c = video_c
        self.video_qs = Video.objects.all()

    def setUp(self):
        self.create_videos()
        self.create_show_with_seasons()
        self.obj_a = Playlist.objects.create(title='test title', video=self.video_a)
        obj_b = Playlist.objects.create(title='test published title',
                                             state=PublishStateOptions.PUBLISHED,
                                             video=self.video_a)
        obj_b.videos.set(self.video_qs)
        obj_b.save()
        self.obj_b = obj_b

    def test_show_has_seasons(self):
        seasons = self.show.playlist_set.all()
        self.assertTrue(seasons.exists())

    def test_video_items(self):
        self.assertEqual(self.obj_b.videos.count(), 3)

    def test_playlist_video(self):
        self.assertEqual(self.obj_a.video, self.video_a)

    def test_playlist_videos_through_model(self):
        v_qs = sorted(list(self.video_qs.values_list("id")))
        video_qs = sorted(list(self.obj_b.videos.all().values_list("id")))
        playlist_item_qs = sorted(list(self.obj_b.playlistitem_set.all().values_list("video")))

        self.assertEqual(v_qs, video_qs, playlist_item_qs)

    def test_video_playlist_id(self):
        ids = self.obj_a.video.get_playlists_ids()
        actual_ids = list(Playlist.objects.filter(video=self.video_a).values_list("id", flat=True))
        self.assertEqual(ids, actual_ids)

    def test_video_playlist(self):
        qs = self.video_a.playlist_featured.all()
        self.assertEqual(qs.count(), 2)

    def test_valid_title(self):
        title = 'test title'
        qs = Playlist.objects.filter(title=title)
        self.assertTrue(qs.exists())

    def test_slug_field(self):
        title = self.obj_a.title
        slug = slugify(title)
        self.assertEqual(self.obj_a.slug, slug)

    def test_created_count(self):
        title = 'test title'
        qs = Playlist.objects.filter(title=title)
        self.assertEqual(qs.count(), 1)

    def test_draft_case(self):
        qs = Playlist.objects.filter(state=PublishStateOptions.DRAFT)
        self.assertEqual(qs.count(), 5)

    def test_published_case(self):
        now = timezone.now()
        published_qs = Playlist.objects.filter(state=PublishStateOptions.PUBLISHED, publish_timestamp__lte=now)
        self.assertTrue(published_qs.exists())

    def test_publish_manager(self):
        published_qs = Playlist.objects.all().published()
        published_qs_2 = Playlist.objects.published()
        self.assertTrue(published_qs.exists())
        self.assertEqual(published_qs.count(), published_qs_2.count())
