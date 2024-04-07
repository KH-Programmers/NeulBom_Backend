from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.utils.translation import gettext_lazy as _
import uuid
from django.utils import timezone


def get_file_path(instance, filename):
    """
    파일 경로와 이름을 생성하는 함수
    """
    filename = filename
    return "card_img/{0}".format(filename)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    objects = UserManager()

    school = [("7010126", "경희고등학교"), ("", "기타")]
    YearOfAdmissionChoice = [
        (2023, "2023년"),
        (2022, "2022년"),
        (2021, "2021년"),
        (2020, "2020년"),
    ]
    role_choices = [("s", "학생"), ("t", "선생님")]

    username = models.CharField(_("아이디"), max_length=150, unique=True)
    name = models.CharField("본명", max_length=10)
    email = models.EmailField("이메일", max_length=255, unique=True, blank=True)
    grade = models.IntegerField("학번", default=0)
    card_img = models.ImageField(upload_to=get_file_path, blank=True)  # 학생증 사진
    barcode_code = models.CharField(max_length=50, blank=True)  # 학생증 바코드

    is_allowed = models.BooleanField(default=False)
    is_staff = models.BooleanField(_("관리자"), default=False)
    is_active = models.BooleanField(default=True)
    role = models.CharField(
        _("학생, 선생님"), max_length=1, choices=role_choices, default="s"
    )

    date_joined = models.DateTimeField(default=timezone.now)
    school = models.CharField(max_length=50, choices=school, default="7010126")  # 학교코드
    YearOfAdmission = models.IntegerField(
        _("입학연도"), choices=YearOfAdmissionChoice, default=2023
    )  # 입학연도

    USERNAME_FIELD = "username"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        db_table = "user"

    def __str__(self):
        return self.username

    def get_barcode_img(self):
        return self.barcode_img

    def get_card_img(self):
        return self.card_img
