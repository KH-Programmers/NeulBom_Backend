from django.urls import path
from . import views

app_name = "studyroomApp"

urlpatterns = [
    path("", views.studyroom.as_view()),
]
