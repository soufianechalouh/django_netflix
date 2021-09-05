from django.test import TestCase
from .models import Playlist, TVShowProxy, MovieProxy


class PlaylistViewTestCase(TestCase):
    fixtures = ["projects"]

    def test_movie_count(self):
        qs = MovieProxy.objects.all()
        self.assertEqual(qs.count(), 5)

    def test_shows_count(self):
        qs = TVShowProxy.objects.all()
        self.assertEqual(qs.count(), 2)

    def test_show_detail_view(self):
        show = TVShowProxy.objects.all().published().first()
        url = show.get_absolute_url()
        self.assertIsNotNone(url)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"{show.title}")
        context = response.context
        obj = context["object"]
        self.assertEqual(obj.id, show.id)

    def test_show_detail_redirect_view(self):
        show = TVShowProxy.objects.all().published().first()
        url = f"/shows/{show.slug}"
        self.assertIsNotNone(url)
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_show_list_view(self):
        shows_qs = TVShowProxy.objects.all().published()
        url = "/shows/"
        self.assertIsNotNone(url)
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        context = response.context
        r_qs = context["object_list"]
        self.assertQuerysetEqual(r_qs.order_by("-timestamp"), shows_qs.order_by("-timestamp"))

    def test_movie_detail_redirect_view(self):
        movie = MovieProxy.objects.all().published().first()
        url = f"/movies/{movie.slug}"
        self.assertIsNotNone(url)
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"{movie.title}")
        context = response.context
        obj = context["object"]
        self.assertEqual(obj.id, movie.id)

    def test_movie_detail_(self):
        movie = MovieProxy.objects.all().published().first()
        url = movie.get_absolute_url()
        self.assertIsNotNone(url)
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_movie_list_view(self):
        movies_qs = MovieProxy.objects.all().published()
        url = "/movies/"
        self.assertIsNotNone(url)
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        context = response.context
        r_qs = context["object_list"]
        self.assertQuerysetEqual(r_qs.order_by("-timestamp"), movies_qs.order_by("-timestamp"))

    def test_search_none_view(self):
        query = None
        response = self.client.get("/search/")
        playlist_qs = Playlist.objects.none()
        self.assertEqual(response.status_code, 200)
        context = response.context
        r_qs = context["object_list"]
        self.assertQuerysetEqual(r_qs.order_by("-timestamp"), playlist_qs.order_by("-timestamp"))
        self.assertContains(response, "Perform a search")

    def test_search_results_view(self):
        query = "comedy"
        response = self.client.get(f"/search/?q={query}")
        playlist_qs = Playlist.objects.all().search(query=query)
        self.assertEqual(response.status_code, 200)
        context = response.context
        r_qs = context["object_list"]
        self.assertQuerysetEqual(r_qs.order_by("-timestamp"), playlist_qs.order_by("-timestamp"))
        self.assertContains(response, f"Search for {query}")
