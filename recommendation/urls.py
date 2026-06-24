from django.urls import path

from . import views

urlpatterns = [
    path("recommend-box/", views.recommend_box_view, name="recommend-box"),
]
