"""URL routes for science search."""

from django.urls import path

from .views import ScienceSearchView

urlpatterns = [
    path("search/", ScienceSearchView.as_view(), name="science-search"),
    path("search", ScienceSearchView.as_view(), name="science-search-noslash"),
]
