from django.contrib import admin
from django.utils import timezone


from .models import (
    Category,
    Tag,
    Article,
    ArticleView,
    Comment,
    ArticleRating,
    CommentLike,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "user",
        "created_at_local",
        "updated_at_local",
    )
    list_filter = (
        "created_at",
        "user",
        "category",
    )
    search_fields = (
        "title",
        "content",
        "user__username",
    )
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("category", "tags")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)

    def created_at_local(self, obj):
        return timezone.localtime(obj.created_at).strftime("%d/%m/%Y %H:%M")

    def updated_at_local(self, obj):
        return timezone.localtime(obj.updated_at).strftime("%d/%m/%Y %H:%M")

    created_at_local.short_description = "Creado el"
    updated_at_local.short_description = "Actualizado el"


@admin.register(ArticleView)
class ArticleViewAdmin(admin.ModelAdmin):
    list_display = ("user", "article", "viewed_at", "ip_adress")
    list_filter = ("viewed_at", "article")
    search_fields = ("user__username", "article__title", "ip_adress")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("user", "article", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "article__title", "content")
    ordering = ("-created_at",)


@admin.register(ArticleRating)
class ArticleRatingAdmin(admin.ModelAdmin):
    list_display = ("user", "article", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("user__username", "article__title")


@admin.register(CommentLike)
class CommentLikeAdmin(admin.ModelAdmin):
    list_display = ("user", "comment", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "comment__content")
