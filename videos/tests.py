from django.test import TestCase

from .models import Video


class VideoModelTestCase(TestCase):
    def setUp(self):
        Video.objects.create(title='test title')

    def test_valid_title(self):
        title = 'test title'
        qs = Video.objects.filter(title=title)
        self.assertTrue(qs.exists())

    def test_created_count(self):
        title = 'test title'
        qs = Video.objects.filter(title=title)
        self.assertEqual(qs.count(), 1)
