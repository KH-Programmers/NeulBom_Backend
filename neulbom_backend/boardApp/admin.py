from django.contrib import admin
from .models import *
from mptt.admin import DraggableMPTTAdmin  # 관리자페이지에서 카테고리를 트리형식으로


class boardAdmin(DraggableMPTTAdmin):
    list_display = ("tree_actions", "indented_title", "id", "board_name", "board_EN")
    list_display_links = ("indented_title",)


class contentModelAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "created_at")


class commentModelAdmin(admin.ModelAdmin):
    list_display = ("id", "content")


admin.site.register(boardModel, boardAdmin)
admin.site.register(contentModel, contentModelAdmin)
admin.site.register(commentModel, commentModelAdmin)
