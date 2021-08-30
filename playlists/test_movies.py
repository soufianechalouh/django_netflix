from django.test import TestCase
from django.utils.text import slugify

from django_netflix.db.models import PublishStateOptions
from videos.models import Video
from .models import MovieProxy


class MovieProxyTestCase(TestCase):

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
        self.movie_title = "test title"
        self.movie_a = MovieProxy.objects.create(title=self.movie_title, video=self.video_a)
        movie_b = MovieProxy.objects.create(title='test published title',
                                             state=PublishStateOptions.PUBLISHED,
                                             video=self.video_a)
        self.published_items_count = 1
        movie_b.videos.set(self.video_qs)
        movie_b.save()
        self.movie_b = movie_b

    def test_movie_video(self):
        self.assertEqual(self.movie_a.video, self.video_a)

    def test_slug_field(self):
        title = self.movie_title
        slug = slugify(title)
        self.assertEqual(self.movie_a.slug, slug)

    def test_valid_title(self):
        title = self.movie_title
        qs = MovieProxy.objects.filter(title=title)
        self.assertTrue(qs.exists())

    def test_draft_case(self):
        qs = MovieProxy.objects.filter(state=PublishStateOptions.DRAFT)
        self.assertEqual(qs.count(), 1)

    def test_publish_manager(self):
        published_qs = MovieProxy.objects.all().published()
        self.assertTrue(published_qs.exists())
        self.assertEqual(published_qs.count(), self.published_items_count)
