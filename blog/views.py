# blog/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from django.utils.text import slugify
from .models import (
    Article,
    Comment,
    ArticleLike,
    ArticleView,
    CommentLike,
)
from .forms import ArticleForm, CommentForm


# Vista para listar todos los artículos (pública)
def article_list(request):
    """
    Vista pública para mostrar todos los artículos ordenados por fecha de creación descendente.
    """
    articles = Article.objects.all().order_by("-created_at")
    return render(request, "blog/article_list.html", {"articles": articles})


def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug)
    comments = article.comments.filter(parent_comment__isnull=True).order_by(
        "-created_at"
    )  # 💡 Filtra solo los comentarios de nivel superior
    comment_form = CommentForm()

    # Nuevo comentario
    if request.method == "POST" and request.user.is_authenticated:
        if "content" in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                new_comment = comment_form.save(commit=False)
                new_comment.article = article
                new_comment.user = request.user

                # Manejar comentarios anidados
                parent_id = request.POST.get(
                    "parent_id"
                )  # <--- Obtener el ID del comentario padre
                if parent_id:
                    try:
                        parent = Comment.objects.get(id=parent_id)
                        new_comment.parent_comment = parent
                    except Comment.DoesNotExist:
                        pass  # Si no encuentra el padre, se ignorará y creará un comentario de nivel superior

                new_comment.save()
                messages.success(request, "Tu comentario ha sido publicado.")
                return redirect("blog:article_detail", slug=article.slug)

    # Registrar vista
    if request.user.is_authenticated:
        ip_address = get_client_ip(request)
        if not ArticleView.objects.filter(
            user=request.user, article=article, ip_adress=ip_address
        ).exists():
            ArticleView.objects.create(
                user=request.user, article=article, ip_adress=ip_address
            )

    # Likes en artículo
    user_has_liked = False
    if request.user.is_authenticated:
        user_has_liked = ArticleLike.objects.filter(
            user=request.user, article=article
        ).exists()

    # 💡 Cálculo de likes en cada comentario
    comments_with_flags = []
    for c in comments:
        c.user_has_liked = False
        if request.user.is_authenticated:
            c.user_has_liked = c.comment_likes.filter(user=request.user).exists()
        comments_with_flags.append(c)

    context = {
        "article": article,
        "comments": comments_with_flags,
        "comment_form": comment_form,
        "user_has_liked": user_has_liked,
        "total_likes": article.total_likes,
    }
    return render(request, "blog/article_detail.html", context)


# Vista para borrar un comentario (NUEVA)
@login_required
def delete_comment(request, comment_id):
    """
    Vista protegida para eliminar un comentario.
    Solo el autor del comentario o un superusuario puede eliminarlo.
    """
    comment = get_object_or_404(Comment, id=comment_id)

    if comment.user != request.user and not request.user.is_superuser:
        messages.error(request, "No tienes permiso para borrar este comentario.")
        return HttpResponseForbidden("Acción no permitida.")

    article_slug = comment.article.slug
    if request.method == "POST":
        comment.delete()
        messages.success(request, "Comentario eliminado exitosamente.")
        return redirect("blog:article_detail", slug=article_slug)

    # Opcional: Renderizar una plantilla de confirmación si se accede por GET
    return render(request, "blog/comment_confirm_delete.html", {"comment": comment})


@login_required
def article_like_toggle(request, pk):
    if request.method == "POST":
        article = get_object_or_404(Article, pk=pk)
        article_like, created = ArticleLike.objects.get_or_create(
            user=request.user, article=article
        )

        if not created:
            article_like.delete()
            is_liked = False
        else:
            is_liked = True

        return JsonResponse({"is_liked": is_liked, "total_likes": article.total_likes})

    return JsonResponse({"error": "Método inválido"}, status=405)


# Vista para crear un nuevo artículo (protegida)
@login_required
def article_create(request):
    """
    Vista protegida para crear un nuevo artículo.
    """
    if request.method == "POST":
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.user = request.user

            # Generar slug único si no se proporciona
            if not article.slug:
                article.slug = slugify(article.title)

            # Asegurar que el slug sea único
            original_slug = article.slug
            counter = 1
            while Article.objects.filter(slug=article.slug).exists():
                article.slug = f"{original_slug}-{counter}"
                counter += 1

            article.save()
            form.save_m2m()  # Guardar relaciones ManyToMany
            messages.success(request, "Artículo creado exitosamente.")
            return redirect("blog:article_detail", slug=article.slug)
    else:
        form = ArticleForm()

    return render(
        request,
        "blog/article_form.html",
        {"form": form, "title": "Crear Nuevo Artículo"},
    )


# Vista para editar un artículo existente (protegida)
@login_required
def article_edit(request, slug):
    """
    Vista protegida para editar un artículo existente.
    Solo el autor del artículo puede editarlo.
    """
    article = get_object_or_404(Article, slug=slug)

    if article.user != request.user:
        messages.error(request, "No tienes permisos para editar este artículo.")
        return HttpResponseForbidden("No tienes permisos para editar este artículo.")

    if request.method == "POST":
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            updated_article = form.save(commit=False)

            # Si el título cambió, actualizar el slug
            if "title" in form.changed_data:
                new_slug = slugify(updated_article.title)
                if new_slug != article.slug:
                    original_slug = new_slug
                    counter = 1
                    while (
                        Article.objects.filter(slug=new_slug)
                        .exclude(pk=article.pk)
                        .exists()
                    ):
                        new_slug = f"{original_slug}-{counter}"
                        counter += 1
                    updated_article.slug = new_slug

            updated_article.save()
            form.save_m2m()
            messages.success(request, "Artículo actualizado exitosamente.")
            return redirect("blog:article_detail", slug=updated_article.slug)
    else:
        form = ArticleForm(instance=article)

    return render(
        request,
        "blog/article_form.html",
        {"form": form, "article": article, "title": f"Editar: {article.title}"},
    )


# Vista para borrar un artículo (protegida)
@login_required
def article_delete(request, slug):
    """
    Vista protegida para eliminar un artículo.
    Solo el autor del artículo puede eliminarlo.
    """
    article = get_object_or_404(Article, slug=slug)

    if article.user != request.user:
        messages.error(request, "No tienes permisos para eliminar este artículo.")
        return HttpResponseForbidden("No tienes permisos para eliminar este artículo.")

    if request.method == "POST":
        article_title = article.title
        article.delete()
        messages.success(
            request, f'El artículo "{article_title}" ha sido eliminado exitosamente.'
        )
        return redirect("blog:my_articles")

    return render(request, "blog/article_confirm_delete.html", {"article": article})


# Vista para mostrar los artículos del usuario actual
@login_required
def my_articles(request):
    """
    Vista protegida para mostrar los artículos del usuario logueado.
    """
    articles = Article.objects.filter(user=request.user)
    return render(request, "blog/my_articles.html", {"articles": articles})



# Función auxiliar para obtener la IP del cliente
def get_client_ip(request):
    """
    Función auxiliar para obtener la IP real del cliente.
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


@login_required
def edit_comment(request, comment_id):
    """
    Vista para editar un comentario en la misma página del artículo.
    Solo el autor puede editarlo.
    """
    comment = get_object_or_404(Comment, id=comment_id)

    if comment.user != request.user and not request.user.is_superuser:
        return HttpResponseForbidden("No tienes permiso para editar este comentario.")

    if request.method == "POST":
        new_content = request.POST.get("content", "").strip()
        if new_content:
            comment.content = new_content
            comment.save()
            messages.success(request, "Comentario editado correctamente.")
        else:
            messages.error(request, "El comentario no puede estar vacío.")
        return redirect("blog:article_detail", slug=comment.article.slug)

    return render(request, "blog/comment_edit_form.html", {"comment": comment})


@login_required
def comment_like_toggle(request, pk):
    """
    Toggle de like en un comentario (AJAX).
    """
    if request.method == "POST":
        comment = get_object_or_404(Comment, pk=pk)
        comment_like, created = CommentLike.objects.get_or_create(
            user=request.user, comment=comment
        )

        if not created:
            comment_like.delete()
            is_liked = False
        else:
            is_liked = True

        return JsonResponse({"is_liked": is_liked, "total_likes": comment.total_likes})

    return JsonResponse({"error": "Invalid request method"}, status=400)


@login_required
def edit_comment_ajax(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if comment.user != request.user and not request.user.is_superuser:
        return JsonResponse(
            {"error": "No tienes permiso para editar este comentario."}, status=403
        )

    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        if not content:
            return JsonResponse(
                {"error": "El comentario no puede estar vacío."}, status=400
            )

        comment.content = content
        comment.save()
        return JsonResponse({"success": True, "content": comment.content})

    return JsonResponse({"error": "Método no permitido"}, status=405)
