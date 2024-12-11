from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import login_or_register_view, profile_view, movements_json,dashboard_view,train

urlpatterns = [
    path("sign/", login_or_register_view, name="signup"),
    path("profile/", profile_view, name='profile'),
    path("movements/<int:martial_art_id>/", movements_json, name="movements_json"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path('dashboard/', dashboard_view, name='dashboard'),
    path("train/", train, name="train"),
]