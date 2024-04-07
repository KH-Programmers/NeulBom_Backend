from django.urls import path
from . import views

app_name = "boardApp"


urlpatterns = [
    path("", views.boardList.as_view()),
    path("popular/", views.trendArticle.as_view()),
    path("all/", views.allArticle.as_view()),
    path("<int:article_pk>/", views.articleDetail.as_view()),
    path("<str:board>/", views.articleList.as_view()),
    path("<str:board>/write/", views.articleWrite.as_view()),
    path("<str:board>/write/<int:article_pk>/", views.articleEdit.as_view()),
    path("<str:board>/<int:article_pk>/", views.articleDetail.as_view()),
    path("<str:board>/<int:article_pk>/<int:comment_pk>/", views.commentEdit.as_view()),
    path("<str:board>/<int:article_pk>/like/", views.articleLike.as_view()),
    path("<str:board>/<int:article_pk>/dislike/", views.articleDislike.as_view()),
    path("<str:board>/<int:article_pk>/vote/", views.voting.as_view()),
    path("<str:board>/<int:article_pk>/vote/<int:voteItemId>/", views.voting.as_view()),
    path('api/search_board/', views.search_board, name='search_board'),
]
