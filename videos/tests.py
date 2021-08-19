from django.test import TestCase
from django.utils import timezone
from django.utils.text import slugify

from .models import Video


class VideoModelTestCase(TestCase):
    def setUp(self):
        self.obj_a = Video.objects.create(title='test title', video_embed_id="abc")
        self.obj_b = Video.objects.create(title='test published title',
                                          state=Video.VideoStateOptions.PUBLISHED,
                                          video_embed_id="def")

    def test_valid_title(self):
        title = 'test title'
        qs = Video.objects.filter(title=title)
        self.assertTrue(qs.exists())

    def test_slug_field(self):
        title = self.obj_a.title
        slug = slugify(title)
        self.assertEqual(self.obj_a.slug, slug)

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
