from django.urls import path
from .views import MartialArtView

urlpatterns = [
    path("martial-art/<slug:slug>/", MartialArtView.as_view(), name="martial_art_detail"),
]