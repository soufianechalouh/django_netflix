from django.http import Http404
from django.utils import timezone
from django.views.generic import ListView, DetailView

from django_netflix.db.models import PublishStateOptions
from .mixins import PlaylistMixin
from .models import Playlist, MovieProxy, TVShowProxy, TVShowSeasonProxy


class SearchView(PlaylistMixin, ListView):

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data()
        query = self.request.GET.get("q")
        if query is not None:
            context["title"] = f"Search for {query}"
        else:
            context["title"] = f"Perform a search"
        return context

    def get_queryset(self):
        request = self.request
        query = request.GET.get("q")
        return Playlist.objects.all().search(query=query)


class MovieListView(PlaylistMixin, ListView):
    queryset = MovieProxy.objects.all()
    title = "Movies"


class MovieDetailView(PlaylistMixin, DetailView):
    template_name = "playlists/movie_detail.html"
    queryset = MovieProxy.objects.all()


class PlaylistDetailView(PlaylistMixin, DetailView):
    template_name = "playlists/playlist_detail.html"
    queryset = Playlist.objects.all()


class TVShowListView(PlaylistMixin, ListView):
    queryset = TVShowProxy.objects.all()
    title = "TV Shows"


class TVShowDetailView(PlaylistMixin, DetailView):
    template_name = "playlists/tvshow_detail.html"
    queryset = TVShowProxy.objects.all()


class TVShowSeasonDetailView(PlaylistMixin, DetailView):
    template_name = "playlists/season_detail.html"
    queryset = TVShowSeasonProxy.objects.all()

    def get_object(self):
        kwargs = self.kwargs
        show_slug = kwargs.get("show_slug")
        season_slug = kwargs.get("season_slug")
        try:
            obj = TVShowSeasonProxy.objects.get(parent__slug__iexact=show_slug,
                                                slug__iexact=season_slug,
                                                state=PublishStateOptions.PUBLISHED,
                                                publish_timestamp__lte=timezone.now())
        except TVShowSeasonProxy.MultipleObjectsReturned:
            qs = TVShowSeasonProxy.objects.filter(parent__slug__iexact=show_slug,
                                                  slug__iexact=season_slug).published()
            obj = qs.first()
        except:
            raise Http404
        return obj


class FeaturedPlaylistListView(PlaylistMixin, ListView):
    template_name = "playlists/featured_list.html"
    queryset = Playlist.objects.featured_playlists()
    title = "Featured"
