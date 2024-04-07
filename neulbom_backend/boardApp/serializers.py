from .models import *
from userApp.models import CustomUser
from rest_framework import serializers


class boardRecursiveField(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class boardSerializer(serializers.ModelSerializer):
    children = boardRecursiveField(many=True)

    class Meta:
        model = boardModel
        fields = (
            "id",
            "board_name",
            "board_EN",
            "children",
        )


class singleboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = boardModel
        fields = ("board_name", "board_EN")

class userSrializer(serializers.ModelSerializer):
    authorName = serializers.ReadOnlyField(
        source="username", read_only=True
    )
    isAdmin = serializers.ReadOnlyField(
        source="is_staff", read_only=True
    )
    class Meta:
        model = CustomUser
        fields = (
            "id",
            "authorName",
            "isAdmin"
        )

class commentSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(read_only=True)
    reply = serializers.SerializerMethodField(read_only=True)

    def get_user(self, obj):
        return userSrializer(obj.author_name).data

    def get_reply(self, obj):
        replies = commentModel.objects.filter(parent_comment=obj)
        serializer = commentSerializer(replies, many=True)
        return serializer.data

    class Meta:
        model = commentModel
        read_only_fields = ("updated_at","user")
        fields = (
            "id",
            "parent_comment",
            "user",
            "content",
            "reply",
            "updated_at",
        )


class voteItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = voteItem
        fields = ["voteId", "text"]


class voteItemField(serializers.Serializer):
    def to_representation(self, instance):
        return voteItem.objects.filter(voteId=instance.id)

    def to_internal_value(self, data):
        return voteItemSerializer(data)


class voteSerializer(serializers.ModelSerializer):
    items = voteItemField(many=True)

    class Meta:
        model = vote
        fields = ["id", "voteTitle", "items"]


class articleSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(read_only=True)
    comments = serializers.SerializerMethodField(read_only=True)
    board_model = serializers.SerializerMethodField(read_only=True)
    updated_at = serializers.SerializerMethodField(read_only=True)
    url = serializers.SerializerMethodField(read_only=True)
    IsLiked = serializers.SerializerMethodField(read_only=True)
    IsOwner = serializers.SerializerMethodField(read_only=True)
    canDelete = serializers.SerializerMethodField(read_only = True)
    IsNotice = serializers.ReadOnlyField(source="isNotice")

    def get_user(self, obj):
        return userSrializer(obj.author_name).data
    
    def get_board_model(self, obj):
        return singleboardSerializer(
            obj.board_model.get_ancestors(ascending=False, include_self=True), many=True
        ).data

    def get_comments(self, obj):
        comments = commentModel.objects.filter(article=obj, parent_comment=None)
        serializer = commentSerializer(comments, many=True)
        return serializer.data

    def get_updated_at(self, obj):
        return obj.updated_at.strftime("%Y-%m-%d %H:%M:%S")

    def get_url(self, obj):
        return f"/board/{obj.board_model.board_EN}/{obj.id}/"

    def get_IsLiked(self, obj):
        liked_user_list = [i for i in obj.liked_users.split(":") if i != ""]
        return str(self.context.get("user_id").id) in liked_user_list

    def get_canDelete(self, obj):
        return obj.author_name == self.context.get("user_id") or self.context.get("user_id").is_staff or self.context.get("user_id").is_superuser

    def get_IsOwner(self, obj):
        return obj.author_name == self.context.get("user_id")

    class Meta:
        model = contentModel
        read_only_fields = (
            "user",
            "viewcounts",
            "like_count",
            "dislike_count",
            "updated_at",
        )
        fields = [
            "id",
            "user",
            "board_model",
            "title",
            "text",
            "vote",
            "comments",
            "viewcounts",
            "like_count",
            "dislike_count",
            "updated_at",
            "url",
            "IsLiked",
            "IsOwner",
            "canDelete",
            "IsNotice"
        ]


class articleListSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(read_only = True)
    IsNotice = serializers.ReadOnlyField(source="isNotice")
    commentCount = serializers.SerializerMethodField(read_only = True)
    viewCounts = serializers.ReadOnlyField(source="viewcounts")
    updatedAt = serializers.ReadOnlyField(source="updated_at")
    likeCount = serializers.ReadOnlyField(source="like_count")

    def get_commentCount(self, obj):
        return commentModel.objects.filter(article=obj).count()
    
    def get_user(self, obj):
        return userSrializer(obj.author_name).data

    class Meta:
        model = contentModel
        read_only_fields = ("user",)
        fields = [
            "id",
            "user",
            "title",
            "commentCount",
            "viewCounts",
            "updatedAt",
            "likeCount",
            "IsNotice"
        ]
