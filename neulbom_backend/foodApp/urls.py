from django.urls import path
from . import views

app_name = "foodApp"

urlpatterns = [
    path("<int:year>/<int:month>/", views.MenuDatasBymonth.as_view()),
    path("<int:year>/<int:month>/<int:day>/", views.MenuDatasByday.as_view()),
    path("<int:date>/<str:vote>/", views.LikeVote.as_view()),
]
