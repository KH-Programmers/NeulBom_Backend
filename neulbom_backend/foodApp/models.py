from django.db import models
from django.conf import settings
from rest_framework import status

# Create your models here.


class menuData(models.Model):
    date = models.PositiveBigIntegerField(primary_key=True)
    lunch_menu_and_allergy = models.TextField(null=True)
    dinner_menu_and_allergy = models.TextField(null=True)

    def lunchVote(self, user: settings.AUTH_USER_MODEL, vote: bool):
        if lunchVoteUsers.objects.filter(date=self, user=user).count() == 0:
            lunchVoteUsers.objects.create(date=self, user=user, likeDislike=vote)
            return status.HTTP_201_CREATED
        elif lunchVoteUsers.objects.filter(date=self, user=user).count() == 1:
            return status.HTTP_202_ACCEPTED
        else:
            print("error")
            return status.HTTP_409_CONFLICT

    def dinnerVote(self, user: settings.AUTH_USER_MODEL, vote: bool):
        if dinnerVoteUsers.objects.filter(date=self, user=user).count() == 0:
            dinnerVoteUsers.objects.create(date=self, user=user, likeDislike=vote)
            return status.HTTP_201_CREATED
        elif dinnerVoteUsers.objects.filter(date=self, user=user).count() == 1:
            return status.HTTP_202_ACCEPTED
        else:
            print("error")
            return status.HTTP_409_CONFLICT

    def LikeDislikeVote(self, user: settings.AUTH_USER_MODEL, vote: str):
        if vote == "lunchLike":
            status = self.lunchVote(user, True)
            return {
                "status": status,
                "amount": lunchVoteUsers.objects.filter(
                    date=self, likeDislike=True
                ).count(),
            }

        elif vote == "lunchDislike":
            status = self.lunchVote(user, False)
            return {
                "status": status,
                "amount": lunchVoteUsers.objects.filter(
                    date=self, likeDislike=False
                ).count(),
            }

        elif vote == "dinnerLike":
            status = self.dinnerVote(user, True)
            return {
                "status": status,
                "amount": dinnerVoteUsers.objects.filter(
                    date=self, likeDislike=True
                ).count(),
            }

        elif vote == "dinnerDislike":
            status = self.dinnerVote(user, False)
            return {
                "status": status,
                "amount": dinnerVoteUsers.objects.filter(
                    date=self, likeDislike=False
                ).count(),
            }


# mealVoteUsers model의 likeDislike field의 True는 좋아요, False는 싫어요를 의미함
class lunchVoteUsers(models.Model):
    date = models.ForeignKey(menuData, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    likeDislike = models.BooleanField()


class dinnerVoteUsers(models.Model):
    date = models.ForeignKey(menuData, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    likeDislike = models.BooleanField()
