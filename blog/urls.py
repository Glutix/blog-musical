# blog/urls.py
from django.urls import path
from . import views

app_name = "blog"

urlpatterns = [
    #! URLs públicas
    path('', views.article_list, name='article_list'),

    #! URL para ver mis artículos
    path('articulo/mis-articulos/', views.my_articles, name='my_articles'),
    
    #! URLs protegidas para CRUD de artículos
    path("articulo/crear/", views.article_create, name="article_create"),
    path("articulo/editar/<slug:slug>/", views.article_edit, name="article_edit"),
    path("articulo/eliminar/<slug:slug>/", views.article_delete, name="article_delete"),

    #! URLs con patron generico
    path('articulo/<slug:slug>/', views.article_detail, name='article_detail'),

    #! Urls que depende del patron generico
    path('articulo/<int:pk>/like/', views.article_like_toggle, name='article_like_toggle'),

    #! CRUD de comentarios
    path('comentario/<int:comment_id>/eliminar/', views.delete_comment, name='comment_delete'),
    path('comentario/<int:comment_id>/editar-ajax/', views.edit_comment_ajax, name='comment_edit_ajax'),
    path('comentario/<int:pk>/like/', views.comment_like_toggle, name='comment_like_toggle'),
    

]
