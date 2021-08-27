from django.views.generic import ListView

from .models import MovieProxy, TVShowProxy


class MovieListView(ListView):
    template_name = "playlist_list.html"
    queryset = MovieProxy.objects.all()


class TVShowView(ListView):
    template_name = "playlist_list.html"
    queryset = TVShowProxy.objects.all()
