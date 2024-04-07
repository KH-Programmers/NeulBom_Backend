from django.urls import path
from . import views

app_name = "calendarApp"

urlpatterns = [
    path("", views.weekEventView.as_view()),
    path("<int:year>/<int:month>/", views.monthEventView.as_view()),
]
