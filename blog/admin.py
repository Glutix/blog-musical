from django.contrib import admin
from django.utils import timezone
from django.utils.text import slugify
# Actualizamos la importación para usar ArticleLike en lugar de ArticleRating
from .models import Category, Tag, Article, ArticleView, Comment, ArticleLike, CommentLike

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'created_at_local', 'updated_at_local']
    list_filter = ['created_at', 'updated_at', 'category', 'tags']
    search_fields = ['title', 'content']
    readonly_fields = ['created_at_local', 'updated_at_local']
    filter_horizontal = ['category', 'tags']
    prepopulated_fields = {'slug': ('title',)}

    fieldsets = (
        ('Main Information', {
            'fields': ('title', 'slug', 'content', 'featured_image')
        }),
        ('Classification', {
            'fields': ('category', 'tags')
        }),
        ('Metadata', {
            'fields': ('user', 'created_at_local', 'updated_at_local'),
            'classes': ('collapse',)
        }),
    )

    def created_at_local(self, obj):
        if obj.created_at:
            local_time = timezone.localtime(obj.created_at)
            return local_time.strftime('%d/%m/%Y %H:%M:%S')
        return '-'
    created_at_local.short_description = 'Created (Local Time)'

    def updated_at_local(self, obj):
        if obj.updated_at:
            local_time = timezone.localtime(obj.updated_at)
            return local_time.strftime('%d/%m/%Y %H:%M:%S')
        return '-'
    updated_at_local.short_description = 'Updated (Local Time)'

    def save_model(self, request, obj, form, change):
        if not obj.slug:
            obj.slug = slugify(obj.title)
        super().save_model(request, obj, form, change)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'article', 'content_preview', 'created_at_local']
    list_filter = ['created_at', 'article']
    search_fields = ['content', 'user__username', 'article__title']
    readonly_fields = ['created_at_local']

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'

    def created_at_local(self, obj):
        if obj.created_at:
            local_time = timezone.localtime(obj.created_at)
            return local_time.strftime('%d/%m/%Y %H:%M:%S')
        return '-'
    created_at_local.short_description = 'Created (Local Time)'

@admin.register(ArticleView)
class ArticleViewAdmin(admin.ModelAdmin):
    list_display = ['user', 'article', 'ip_adress', 'viewed_at_local']
    list_filter = ['viewed_at', 'article']
    search_fields = ['user__username', 'article__title', 'ip_adress']
    readonly_fields = ['viewed_at_local']

    def viewed_at_local(self, obj):
        if obj.viewed_at:
            local_time = timezone.localtime(obj.viewed_at)
            return local_time.strftime('%d/%m/%Y %H:%M:%S')
        return '-'
    viewed_at_local.short_description = 'Viewed (Local Time)'

# Actualizamos el decorador y el nombre de la clase para usar ArticleLike
@admin.register(ArticleLike)
class ArticleLikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'article', 'created_at_local']
    list_filter = ['created_at']
    search_fields = ['user__username', 'article__title']
    readonly_fields = ['created_at_local']

    def created_at_local(self, obj):
        if obj.created_at:
            local_time = timezone.localtime(obj.created_at)
            return local_time.strftime('%d/%m/%Y %H:%M:%S')
        return '-'
    created_at_local.short_description = 'Liked (Local Time)'

@admin.register(CommentLike)
class CommentLikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'comment', 'created_at_local']
    list_filter = ['created_at']
    search_fields = ['user__username']
    readonly_fields = ['created_at_local']

    def created_at_local(self, obj):
        if obj.created_at:
            local_time = timezone.localtime(obj.created_at)
            return local_time.strftime('%d/%m/%Y %H:%M:%S')
        return '-'
    created_at_local.short_description = 'Liked (Local Time)'
