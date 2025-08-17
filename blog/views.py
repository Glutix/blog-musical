# blog/views.py
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from django.db.models import Count
from django.utils.text import slugify
from .models import (
    Article,
    Comment,
    ArticleLike,
    ArticleView,
    CommentLike,
    Category,
)
from .forms import ArticleForm, CommentForm
from user_auth.models import Profile
from django.conf import settings
from django.core.mail import send_mail

# import json


def custom_404_view(request, exception):
    """
    Vista personalizada para manejar el error 404 (página no encontrada).
    """
    return render(request, "404.html", status=404)


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
        # Soporte para AJAX (JSON) y POST normal
        if request.content_type == "application/json":
            data = json.loads(request.body)
            content = data.get("content", "").strip()
            parent_id = data.get("parent_id")
        else:
            content = request.POST.get("content", "").strip()
            parent_id = request.POST.get("parent_id")
        if content:
            comment_form = CommentForm({"content": content})
            if comment_form.is_valid():
                new_comment = comment_form.save(commit=False)
                new_comment.article = article
                new_comment.user = request.user
                if parent_id:
                    try:
                        parent = Comment.objects.get(id=parent_id)
                        new_comment.parent_comment = parent
                    except Comment.DoesNotExist:
                        pass
                new_comment.save()
                if (
                    request.headers.get("x-requested-with") == "XMLHttpRequest"
                    or request.content_type == "application/json"
                ):
                    from django.template.loader import render_to_string

                    # Pasa el contexto completo de request.user y user al render, para que los hijos tengan el CSRF token y clase
                    context = {
                        "comment": new_comment,
                        "user": request.user,
                        "request": request,
                    }
                    comment_html = render_to_string(
                        "blog/partials/comment.html", context, request=request
                    )
                    return JsonResponse({"success": True, "comment_html": comment_html})
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

    # 💡 Cálculo de likes en cada comentario y replies recursivamente
    def set_user_has_liked(comment, user):
        comment.user_has_liked = False
        if user.is_authenticated:
            comment.user_has_liked = comment.comment_likes.filter(user=user).exists()
        # Recursivo para replies (forzar lista para evitar problemas de queryset en template)
        replies = list(comment.replies.all())
        comment.replies_list = replies  # atributo público para el template
        for reply in replies:
            set_user_has_liked(reply, user)

    comments_with_flags = []
    for c in comments:
        set_user_has_liked(c, request.user)
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

            # Lógica para atribuir el rol de autor al crear el primer artículo
            if Article.objects.filter(user=request.user).count() == 1:
                try:
                    profile = Profile.objects.get(user=request.user)
                    profile.is_author = True
                    profile.save()
                    messages.success(
                        request, "¡Felicidades! Se te ha atribuido el rol de autor."
                    )
                except Profile.DoesNotExist:
                    messages.warning(
                        request,
                        "Perfil de usuario no encontrado. No se pudo actualizar el rol de autor.",
                    )

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
        if request.content_type == "application/json":
            data = json.loads(request.body)
            content = data.get("content", "").strip()
        else:
            content = request.POST.get("content", "").strip()
        if not content:
            return JsonResponse(
                {"error": "El comentario no puede estar vacío."}, status=400
            )

    comment.content = content
    comment.save()
    from django.template.loader import render_to_string

    content_html = render_to_string(
        "blog/partials/comment_content.html", {"comment": comment}
    )
    return JsonResponse({"success": True, "content_html": content_html})


@login_required
def delete_comment_ajax(request, comment_id):
    """
    Vista para eliminar un comentario vía AJAX.
    Devuelve una respuesta JSON para ser manejada por el frontend.
    """
    comment = get_object_or_404(Comment, id=comment_id)

    # Comprobar permisos: solo el autor o un superusuario pueden eliminar
    if comment.user != request.user and not request.user.is_superuser:
        return JsonResponse(
            {"error": "No tienes permiso para eliminar este comentario."}, status=403
        )

    if request.method == "POST":
        comment.delete()
        return JsonResponse({"success": True})

    # Si no es POST, devolver un error
    return JsonResponse({"error": "Método no permitido."}, status=405)


def articles_by_category(request, category_name):
    """
    Vista pública para mostrar artículos filtrados por una categoría específica.
    """
    # Usamos get_object_or_404 para devolver un 404 si la categoría no existe
    category = get_object_or_404(Category, name=category_name)
    # Filtramos los artículos que tienen esa categoría.
    articles = Article.objects.filter(category__name=category_name).order_by(
        "-created_at"
    )

    # Pasamos la categoría y los artículos a la plantilla.
    # El título se actualizará dinámicamente.
    return render(
        request,
        "blog/articles_by_category.html",
        {
            "articles": articles,
            "category": category,
        },
    )


def category_list(request):
    """
    Vista pública para mostrar las categorías con un recuento de artículos.
    """
    # Anotamos cada categoría con el recuento de artículos y luego ordenamos.
    categories = Category.objects.annotate(article_count=Count("articles")).order_by(
        "-article_count", "name"
    )
    return render(request, "blog/category_list.html", {"categories": categories})


#! Vista para manejar el formulario de contacto
def contact(request):
    # Variable de control para mostrar el mensaje "enviado" en el template
    enviado = False

    # Si el usuario envió el formulario (método POST)...
    if request.method == "POST":
        # Toma los valores enviados por el formulario mediante sus 'name'
        nombre = request.POST.get("nombre")
        email = request.POST.get("email")
        mensaje = request.POST.get("mensaje")

        # Arma el asunto del correo incluyendo el nombre del remitente
        asunto = f"Nuevo mensaje de contacto - {nombre}"

        # Cuerpo del correo: incluye nombre, email y el mensaje
        cuerpo = f"Nombre: {nombre}\n" f"Email: {email}\n\n" f"Mensaje:\n{mensaje}"

        # Envía el correo:
        # send_mail(
        #   subject,              -> Asunto del correo
        #   message,              -> Texto plano del correo
        #   from_email,           -> Dirección del remitente (debe existir y estar autorizada)
        #   recipient_list,       -> Lista de destinatarios (una o varias direcciones)
        #   fail_silently=False   -> Si hay error, lanza excepción (útil para detectar problemas)
        # )
        send_mail(
            asunto,
            cuerpo,
            settings.DEFAULT_FROM_EMAIL,  # Remitente (definido en settings.py)
            [settings.CONTACT_EMAIL],  # Lista de destinatarios (el correo del blog)
            fail_silently=False,
        )

        # Marca que el envío se realizó para que el template muestre el mensaje de éxito
        enviado = True

    # Renderiza la plantilla 'contacto.html' pasando la variable 'enviado'
    return render(request, "blog/contact.html", {"enviado": enviado})


#! About
def about(request):
    return render(request, "blog/about.html")
