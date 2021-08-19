from django.test import TestCase
from django.utils import timezone

from .models import Video


class VideoModelTestCase(TestCase):
    def setUp(self):
        Video.objects.create(title='test title')
        Video.objects.create(title='test published title', state=Video.VideoStateOptions.PUBLISHED)

    def test_valid_title(self):
        title = 'test title'
        qs = Video.objects.filter(title=title)
        self.assertTrue(qs.exists())

    def test_created_count(self):
        title = 'test title'
        qs = Video.objects.filter(title=title)
        self.assertEqual(qs.count(), 2)

    def test_draft_case(self):
        qs = Video.objects.filter(state=Video.VideoStateOptions.DRAFT)
        self.assertEqual(qs.count(), 1)

    def test_published_case(self):
        now = timezone.now()
        published_qs = Video.objects.filter(state=Video.VideoStateOptions.PUBLISHED, publish_timestamp__lte=now)
        self.assertTrue(published_qs.exists())
