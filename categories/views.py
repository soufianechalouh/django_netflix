from django.db.models import Count
from django.http import Http404
from django.views.generic import ListView, DetailView
from playlists.models import Playlist
from .models import Category
from playlists.mixins import PlaylistMixin


class CategoryListView(ListView):
    queryset = Category.objects.all().filter(active=True).annotate(pl_count=Count("playlists")).filter(pl_count__gt=0)


class CategoryDetailView(PlaylistMixin, ListView):
    """
    Another list view for playlists
    """
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        try:
            obj = Category.objects.get(slug=self.kwargs.get("slug"))
        except Category.DoesNotExist:
            return Http404
        except Category.MultipleObjectsReturned:
            return Http404
        except:
            obj = None

        context["object"] = obj
        if obj is not None:
            context["title"] = obj.title

        return context

    def get_queryset(self):
        slug = self.kwargs.get("slug")
        return Playlist.objects.filter(category__slug=slug).movie_or_show()

