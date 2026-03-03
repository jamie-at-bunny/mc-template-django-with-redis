from django.urls import path

from kv import views

urlpatterns = [
    path("", views.root),
    path("kv/<str:key>", views.kv),
]
