from django.test import TestCase
from django.utils import timezone
from django.utils.text import slugify

from django_netflix.db.models import PublishStateOptions
from .models import Playlist


class PlaylistModelTestCase(TestCase):
    def setUp(self):
        self.obj_a = Playlist.objects.create(title='test title')
        self.obj_b = Playlist.objects.create(title='test published title', state=PublishStateOptions.PUBLISHED)

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
        self.assertEqual(qs.count(), 1)

    def test_published_case(self):
        now = timezone.now()
        published_qs = Playlist.objects.filter(state=PublishStateOptions.PUBLISHED, publish_timestamp__lte=now)
        self.assertTrue(published_qs.exists())

    def test_publish_manager(self):
        published_qs = Playlist.objects.all().published()
        published_qs_2 = Playlist.objects.published()
        self.assertTrue(published_qs.exists())
        self.assertEqual(published_qs.count(), published_qs_2.count())
