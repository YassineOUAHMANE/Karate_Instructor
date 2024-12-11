from django.urls import path
from .views import HomeView, AboutView, ContactView, programs_view, TeamView
urlpatterns = [
    path("", HomeView.as_view(), name='home'),
    path("about/", AboutView.as_view(), name='about'),
    path("contact/", ContactView.as_view(), name='contact'),
    path("programs/", programs_view, name="programs"),
    path("team/", TeamView.as_view(), name="team"),   
]