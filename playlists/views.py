from django.views.generic import ListView

from .models import MovieProxy, TVShowProxy


class PlaylistMixin():
    title = None
    template_name = "playlist_list.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        if self.title is not None:
            context["title"] = self.title
        return context


class MovieListView(PlaylistMixin, ListView):
    queryset = MovieProxy.objects.all()
    title = "Movies"


class TVShowView(PlaylistMixin, ListView):
    queryset = TVShowProxy.objects.all()
    title = "TV Shows"
