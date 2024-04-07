from django.db import models
from django.conf import settings
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from mptt.managers import TreeManager
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q

# 투표 항목
class voteItem(models.Model):
    voteId = models.ForeignKey("vote", on_delete=models.CASCADE, related_name="item")
    text = models.CharField(max_length=64)

    def itemVoteCount(self) -> int:
        return voteUsers.objects.filter(itemId=self).count()

# 유저가 투표한 것
class voteUsers(models.Model):
    itemId = models.ForeignKey(
        "voteItem", on_delete=models.CASCADE, related_name="voteItem"
    )
    userId = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="voteUser"
    )

class CategoryManager(TreeManager):
    def viewable(self):
        queryset = self.get_queryset().filter(level=0)
        return queryset


class boardModel(MPTTModel):
    objects = CategoryManager()
    board_name = models.CharField(max_length=20)
    board_EN = models.CharField(max_length=50, null=False)
    anonymous = models.BooleanField(default=False)
    parent = TreeForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="children",
        db_index=True,
        on_delete=models.CASCADE,
    )


class contentModel(models.Model):
    def __str__(self):
        return str(self.id)

    author_name = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="contents"
    )
    title = models.CharField(max_length=2000, null=False)
    text = models.TextField(null=False)
    board_model = models.ForeignKey(boardModel, on_delete=models.CASCADE)
    vote = models.ForeignKey("vote", on_delete=models.SET_NULL, null=True, blank=True)
    viewcounts = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    like_count = models.IntegerField(default=0)
    dislike_count = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)
    liked_users = models.TextField(default="")
    isNotice = models.BooleanField(default=False)
    IsDeleted = models.BooleanField(default=False)


class commentModel(models.Model):
    article = models.ForeignKey(
        contentModel, on_delete=models.CASCADE, related_name="comments"
    )
    author_name = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    parent_comment = models.ForeignKey("self", on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.content


# 투표 본체
class vote(models.Model):
    voteTitle = models.CharField(max_length=64)

    # 자신이 가질 투표 아이템들을 만든다. -> serializer를 사용하며 더미데이터화?
    def createItems(self, items: list) -> None:
        for i in items:
            voteItem.objects.create(voteId=self, text=i)

    # 모든 자신이 가지는 투표 아이템들을 가져온다.
    def getAllItems(self):
        return list(voteItem.objects.filter(voteId=self))

    # 모든 자신이 가지는 투표 아이템들을 가공해서 가져온다.
    def getVote(
        self,
    ):  # -> dict['id':int, 'title':str, 'itmes':list[dict['amount':int, 'text':str]], 'amount':int]
        voteInfo = {"id": self.id, "title": self.voteTitle, "items": [], "amount": 0}
        for i in self.getAllItems():
            amount = i.itemVoteCount()
            voteInfo["items"].append({"amount": amount, "text": i.text, "id": i.id})
            voteInfo["amount"] += amount
        return voteInfo

    # 자신이 가지는 모든 투표 아이템들의 아이디를 가져온다. -> 더미데이터
    def getAllItemIds(self):  # -> list[int]
        itemId = []
        for i in list(voteItem.objects.filter(voteId=self)):
            itemId.append(i.id)
        return itemId

    # 투표 했을 때 투표한 기록이 없다면 투표 후 201, 있다면 409.
    def voting(self, voteItemId: int, user: settings.AUTH_USER_MODEL):
        if not self.checkUserVote(user=user, items=self.getAllItems()):
            voteUsers.objects.create(
                itemId=voteItem.objects.get(id=voteItemId), userId=user
            )
            return status.HTTP_201_CREATED
        else:
            return status.HTTP_409_CONFLICT

    # 받은 uid에 해당하는 투표 기록을 확인한다.
    def checkUserVote(self, user: settings.AUTH_USER_MODEL, items: list, n=0) -> bool:
        if len(items) == n:
            return False
        try:
            voteUsers.objects.get(itemId=items[n], userId=user)
            return True
        except:
            return self.checkUserVote(user, items, n + 1)

# API 뷰 함수
@api_view(['GET'])
def search_board(request):
    # 검색어를 가져옴
    search_query = request.GET.get('q', '')

    # 게시판 검색 쿼리를 작성
    # board_name 또는 board_EN 필드에서 검색어를 포함하는 게시판을 찾음
    search_filter = Q(board_name__icontains=search_query) | Q(board_EN__icontains=search_query)

    # 게시판을 검색
    boards = boardModel.objects.filter(search_filter)

    # 검색 결과를 시리얼라이즈 또는 다른 형식으로 변환할 수 있음
    # 여기서는 간단하게 게시판 이름만 추출하여 리스트에 저장
    search_results = [board.board_name for board in boards]

    # 검색 결과를 반환
    return Response(search_results, status=status.HTTP_200_OK)
