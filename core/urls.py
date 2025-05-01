from django.urls import path

from .views import FindMissingPersonView

urlpatterns = [
    path("find/", FindMissingPersonView.as_view()),
]
