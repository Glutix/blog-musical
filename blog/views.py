# blog/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import Http404, HttpResponseForbidden
from django.utils.text import slugify
from .models import Article, Category, Tag
from .forms import ArticleForm


# Create your views here.
# Vista para listar todos los artículos (pública)
def article_list(request):
    """
    Vista pública para mostrar todos los artículos ordenados por fecha de creación descendente.
    """
    # Obtener todos los artículos y ordenarlos por el campo 'created_at' de forma descendente
    articles = Article.objects.all().order_by("-created_at")

    return render(request, "blog/article_list.html", {"articles": articles})


# Vista para mostrar un artículo específico (pública)
def article_detail(request, slug):
    """
    Vista pública para mostrar un artículo específico
    También registra las vistas por IP única
    """
    article = get_object_or_404(Article, slug=slug)

    # Registrar vista por IP única
    if request.user.is_authenticated:
        from .models import ArticleView

        ip_address = get_client_ip(request)

        # Verificar si ya existe una vista de este usuario/IP para este artículo
        existing_view = ArticleView.objects.filter(
            user=request.user, article=article, ip_adress=ip_address
        ).first()

        if not existing_view:
            ArticleView.objects.create(
                user=request.user, article=article, ip_adress=ip_address
            )

    # Obtener comentarios del artículo
    comments = article.comment_set.all()

    context = {
        "article": article,
        "comments": comments,
    }
    return render(request, "blog/article_detail.html", context)


# Vista para crear un nuevo artículo (protegida)
@login_required
def article_create(request):
    """
    Vista protegida para crear un nuevo artículo.
    Solo usuarios autenticados pueden crear artículos.
    """
    if request.method == "POST":
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            # Asignar automáticamente el usuario logueado como autor
            article.user = request.user

            # Generar slug único si no se proporciona
            if not article.slug:
                article.slug = slugify(article.title)

            # Verificar que el slug sea único
            original_slug = article.slug
            counter = 1
            while Article.objects.filter(slug=article.slug).exists():
                article.slug = f"{original_slug}-{counter}"
                counter += 1

            article.save()
            form.save_m2m()  # Guardar relaciones ManyToMany (categorías y tags)

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

    # Verificar que el usuario actual sea el autor del artículo
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
                    # Verificar que el nuevo slug sea único
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
            form.save_m2m()  # Guardar relaciones ManyToMany

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

    # Verificar que el usuario actual sea el autor del artículo
    if article.user != request.user:
        messages.error(request, "No tienes permisos para eliminar este artículo.")
        return HttpResponseForbidden("No tienes permisos para eliminar este artículo.")

    if request.method == "POST":
        article_title = article.title
        article.delete()
        messages.success(
            request, f'El artículo "{article_title}" ha sido eliminado exitosamente.'
        )
        # Se ha cambiado la redirección para que apunte a la página de los artículos del usuario
        return redirect("blog:my_articles")

    return render(request, "blog/article_confirm_delete.html", {"article": article})


# Vista para mostrar los artículos del usuario actual
@login_required
def my_articles(request):
    """
    Vista protegida para mostrar los artículos del usuario logueado
    """
    articles = Article.objects.filter(user=request.user)
    return render(request, "blog/my_articles.html", {"articles": articles})


# Función auxiliar para obtener la IP del cliente
def get_client_ip(request):
    """
    Función auxiliar para obtener la IP real del cliente
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip

