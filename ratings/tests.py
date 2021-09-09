import random

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.db.models import Avg

from playlists.models import Playlist
from .models import Rating, RatingChoices

User = get_user_model()


class RatingTestCase(TestCase):

    def create_playlists(self):
        items = []
        self.playlist_count = random.randint(10, 100)
        for i in range(self.playlist_count):
            items.append(Playlist(title=f"TV show {i}"))
        Playlist.objects.bulk_create(items)
        self.playlists = Playlist.objects.all()

    def create_users(self):
        items = []
        self.user_count = random.randint(10, 100)
        for i in range(self.user_count):
            items.append(User(username=f"user_{i}"))
        User.objects.bulk_create(items)
        self.users = User.objects.all()

    def create_ratings(self):
        items = []
        self.ratings_count = 100
        self.ratings_totals = []
        for i in range(self.ratings_count):
            user = self.users.order_by("?").first()
            ply_obj = self.playlists.order_by("?").first()
            rating_val = random.choice(RatingChoices.choices)[0]
            if rating_val:
                self.ratings_totals.append(rating_val)
            items.append(
                Rating(
                    user=user,
                    content_object=ply_obj,
                    value=rating_val
                )
            )
        Rating.objects.bulk_create(items)
        self.ratings = Rating.objects.all()

    def setUp(self):
        self.create_users()
        self.create_playlists()
        self.create_ratings()

    def test_user_count(self):
        qs = User.objects.all()
        self.assertTrue(qs.exists())
        self.assertEqual(qs.count(), self.user_count)
        self.assertEqual(self.users.count(), self.user_count)

    def test_playlist_count(self):
        qs = Playlist.objects.all()
        self.assertTrue(qs.exists())
        self.assertEqual(qs.count(), self.playlist_count)

    def test_rating_count(self):
        qs = Rating.objects.all()
        self.assertTrue(qs.exists())
        self.assertEqual(qs.count(), self.ratings_count)
        self.assertEqual(self.ratings.count(), self.ratings_count)

    def test_rating_agg(self):
        db_average = Rating.objects.aggregate(average=Avg("value"))["average"]
        self.assertIsNotNone(db_average)
        self.assertTrue(db_average > 0)
        total_sum = sum(self.ratings_totals)
        average = total_sum / (len(self.ratings_totals)* 1.0)
        self.assertEqual(average, db_average)

    def test_rating_playlist_agg(self):
        item_1 = Playlist.objects.aggregate(average=Avg("ratings__value"))["average"]
        self.assertIsNotNone(item_1)
        self.assertTrue(item_1 > 0)


