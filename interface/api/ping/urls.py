from django.urls import path

from . import views

urlpatterns = [
    path("api/ping/", views.ping, name="ping"),
]
