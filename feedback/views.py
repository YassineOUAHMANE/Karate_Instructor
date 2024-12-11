from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import MartialArt


class MartialArtView (LoginRequiredMixin, DetailView) : 
    model = MartialArt
    template_name = "feedback/martial_art_detail.html"
    context_object_name = "martial_art"
