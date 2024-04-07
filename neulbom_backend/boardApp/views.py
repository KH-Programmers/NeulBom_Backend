from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import *
from .serializers import *
from .permissions import Is_Owner_or_Admin
from django.utils import timezone
from itertools import chain

# 게시판 목록 요청
class boardList(APIView):
    def get(self, request):
        boards = boardModel.objects.viewable()
        serializer = boardSerializer(boards, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = boardSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def get_Notice(article_list):
    return list(chain(contentModel.objects.filter(isNotice=True, IsDeleted=False), article_list))

def get_articleList(board, sort):
    board = get_object_or_404(boardModel, board_EN=board)
    if board.is_leaf_node():
        article_list = contentModel.objects.filter(board_model=board, IsDeleted=False)
    else:
        boards = board.get_leafnodes()
        article_list = contentModel.objects.filter(board_model__in=boards, IsDeleted=False)

    if sort == "likes":
        article_list =  article_list.order_by("-like_count", "-id")
    elif sort == "comments":
        article_list =  article_list.order_by("-comment_count", "-id")
    elif sort == "viewcounts":
        article_list =  article_list.order_by("-viewcounts", "-id")
    else:
        article_list =  article_list.order_by("-id")
    return get_Notice(article_list)


# 글 목록, 게시판 삭제 요청
class articleList(APIView):
    def get(self, request, board):
        sort = request.query_params.get("sort", "")
        article_list = get_articleList(board,sort)
        serializer = articleListSerializer(article_list, many=True)
        return Response(serializer.data)

    def delete(self, request, board):
        board = get_object_or_404(boardModel, board_EN=board)
        board.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class allArticle(APIView):
    def get(slef, request):
        sort = request.query_params.get("sort", "")
        article_list = contentModel.objects.filter(IsDeleted=False)
        if sort == "likes":
            article_list = article_list.order_by("-like_count", "-id")
        elif sort == "comments":
            article_list = article_list.order_by("-comment_count", "-id")
        elif sort == "viewcounts":
            article_list = article_list.order_by("-viewcounts", "-id")
        else:
            article_list = article_list.order_by("-id")
        article_list = get_Notice(article_list)
        serializer = articleListSerializer(article_list, many=True)
        return Response(serializer.data)


# 인기글 목록 요청
class trendArticle(APIView):
    def get(self, request):
        article_list = contentModel.objects.filter(like_count__gte=10, IsDeleted=False).order_by("-id")
        serializer = articleListSerializer(article_list, many=True)
        return Response(serializer.data)


# 메인 페이지용 인기글 목록 요청
def getTrendArticles():
    article_list = contentModel.objects.filter(like_count__gte=10, IsDeleted=False).order_by("-id")[:10]
    article_list = get_Notice(article_list)
    serializer = articleListSerializer(article_list, many=True)
    return serializer.data


# 글 열람, 삭제 / 댓글 작성 요청
class articleDetail(APIView):
    permission_classes = [Is_Owner_or_Admin]

    def get(self, request, board, article_pk):
        article = get_object_or_404(contentModel, pk=article_pk)
        article.viewcounts += 1
        article.save()
        serializer = articleSerializer(
            article, context={"user_id": request.user}
        )
        return Response(serializer.data)

    def delete(self, request, board, article_pk):
        article = get_object_or_404(contentModel, pk=article_pk)
        article.IsDeleted = True
        article.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def post(self, request, board, article_pk):
        serializer = commentSerializer(data=request.data)
        article = get_object_or_404(contentModel, pk=article_pk)
        if serializer.is_valid():
            article.comment_count += 1
            serializer.save(author_name=self.request.user, article_id=article_pk)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 글 작성 요청
class articleWrite(APIView):
    def post(self, request, board):
        serializer = articleSerializer(data=request.data, context={"user_id": request.user})
        if serializer.is_valid():
            serializer.save(
                author_name=self.request.user,
                board_model=get_object_or_404(boardModel, board_EN=board),
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 글 수정 요청
class articleEdit(APIView):
    permission_classes = [Is_Owner_or_Admin]

    def get(self, request, board, article_pk):
        article = get_object_or_404(contentModel, pk=article_pk)
        serializer = articleSerializer(article, context={"user_id": request.user})
        return Response(serializer.data)

    def put(self, request, board, article_pk):
        serializer = get_object_or_404(contentModel, pk=article_pk)
        if serializer.is_valid():
            serializer.save(
                author_name=self.request.user,
                board_model=get_object_or_404(boardModel, board_EN=board),
                update_at=timezone.now(),
            )
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 댓글 수정, 삭제 요청
class commentEdit(APIView):
    permission_classes = [Is_Owner_or_Admin]
    def get(self, request, board, article_pk, comment_pk):
        comment = get_object_or_404(commentModel, pk=comment_pk)
        serializers = commentSerializer(comment)
        return Response(serializers.data)
    def put(self, requset, board, article_pk, comment_pk):
        comment = get_object_or_404(commentModel, pk=comment_pk)
        serializer = commentSerializer(comment, requset.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.erros, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, board, article_pk, comment_pk):
        article = get_object_or_404(commentModel, pk=comment_pk)
        article.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# 좋아요 싫어요 요청
class articleLike(APIView):
    def get(self, request, board, article_pk):
        article = get_object_or_404(contentModel, pk=article_pk)
        liked_user_list = [i for i in article.liked_users.split(":") if i != ""]
        if str(request.user.id) in liked_user_list:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            article.like_count += 1
            liked_user_list.append(request.user.id)
            article.liked_users = ":".join(map(str, liked_user_list))
            article.save()
            serializer = articleSerializer(article, context={"user_id": request.user})
            return Response(serializer.data)


class articleDislike(APIView):
    def get(self, request, board, article_pk):
        article = get_object_or_404(contentModel, pk=article_pk)
        article.dislike_count += 1
        article.save()
        serializer = articleSerializer(article, context={"user_id": request.user})
        return Response(serializer.data)


class voteMake(APIView):
    def post(self, request):
        if len(request.data.getlist("voteItemText")) >= 2:
            serializers = voteSerializer(data=request.data)
            serializers.save()
            return Response(
                status=status.HTTP_201_CREATED, data={"voteId": serializers.id}
            )
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class voting(APIView):
    def get(self, request, board, article_pk, voteItemId):
        if request.user.is_authenticated:
            return Response(
                status=vote.objects.get(id=voteItemId).voting(
                    voteItemId=request.data["voteSelect"], userId=request.user
                )
            )
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
