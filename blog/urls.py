# blog/urls.py
from django.urls import path
from . import views

app_name = "blog"

urlpatterns = [
    # URLs públicas
    path("", views.article_list, name="article_list"),
    path("articulo/<slug:slug>/", views.article_detail, name="article_detail"),
    # URLs protegidas para CRUD de artículos
    path("crear/", views.article_create, name="article_create"),
    path("editar/<slug:slug>/", views.article_edit, name="article_edit"),
    path("eliminar/<slug:slug>/", views.article_delete, name="article_delete"),
    # URL para ver mis artículos
    path("mis_articulos/", views.my_articles, name="mis_articulos"),
]
