# blog/models.py
from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    featured_image = CloudinaryField('image')
    slug = models.SlugField(unique=True, max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="articles")
    category = models.ManyToManyField(Category, blank=True, related_name="articles")
    tags = models.ManyToManyField(Tag, blank=True, related_name="articles")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Article"
        verbose_name_plural = "Articles"

    def __str__(self):
        return self.title

    @property
    def total_likes(self):
        return self.likes.count()


class ArticleView(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)
    ip_adress = models.CharField(max_length=45)

    class Meta:
        verbose_name = "Article View"
        verbose_name_plural = "Article views"


class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Comment"
        verbose_name_plural = "Comments"

    def __str__(self):
        return f"Comentado por {self.user.username} en: {self.article.title}"

    @property
    def total_likes(self):
        return self.comment_likes.count()


class ArticleLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="article_likes")
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "article")
        verbose_name = "Article Like"
        verbose_name_plural = "Article Likes"

    def __str__(self):
        return f"{self.user.username} le gusta {self.article.title}"


class CommentLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comment_likes")
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="comment_likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "comment")
        verbose_name = "Like in Comment"
        verbose_name_plural = "Like in Comments"
