from django.shortcuts import render
from django.views import View
from django.views.generic import ListView, DetailView
from playlists.models import Playlist
from playlists.mixins import PlaylistMixin

from .models import TaggedItem


class TaggedItemListView(View):
    def get(self, request):
        tags_list = TaggedItem.objects.unique_list()
        context = {
            "tags_list": tags_list
        }
        return render(request, "tags/tags_list.html", context)


class TaggedItemDetailView(PlaylistMixin, ListView):
    """
    Another list view for playlists
    """

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context["title"] = f"{self.kwargs.get('slug')}"
        return context

    def get_queryset(self):
        tag = self.kwargs.get("tag")
        return Playlist.objects.filter(tags__tag=tag).movie_or_show()
