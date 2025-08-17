# blog/urls.py
from django.urls import path
from . import views

app_name = "blog"

urlpatterns = [
    #! URLs públicas
    path('', views.article_list, name='article_list'),
    path('catalogo/', views.category_list, name='category_list'),
    path('catalogo/<str:category_name>/', views.articles_by_category, name='articles_by_category'),

    #! URL para ver mis artículos
    path('articulo/mis-articulos/', views.my_articles, name='my_articles'),
    
    #! URLs protegidas para CRUD de artículos
    path("articulo/crear/", views.article_create, name="article_create"),
    path("articulo/editar/<slug:slug>/", views.article_edit, name="article_edit"),
    path("articulo/eliminar/<slug:slug>/", views.article_delete, name="article_delete"),

    # Rutas de Artículos
    path('articulo/<slug:slug>/', views.article_detail, name='article_detail'),
    path('articulo/<int:pk>/like/', views.article_like_toggle, name='article_like_toggle'),
    
    # Rutas de Comentarios (AQUÍ ESTÁN LAS CORRECCIONES Y ADICIONES)
    path('comentario/<int:pk>/like/', views.comment_like_toggle, name='comment_like_toggle'),
    path('comentario/<int:comment_id>/editar-ajax/', views.edit_comment_ajax, name='edit_comment_ajax'),
    
    # ¡NUEVA RUTA PARA EL BORRADO CON AJAX!
    path('comentario/<int:comment_id>/eliminar-ajax/', views.delete_comment_ajax, name='comment_delete_ajax'),

    # Ruta original de borrado (puedes mantenerla como fallback o eliminarla si solo usarás AJAX)
    path('comentario/<int:comment_id>/eliminar/', views.delete_comment, name='comment_delete'),
    
    # ... (rutas para crear, editar, eliminar artículos, etc.)
    path('crear/', views.article_create, name='article_create'),
    path('editar/<slug:slug>/', views.article_edit, name='article_edit'),
    path('eliminar/<slug:slug>/', views.article_delete, name='article_delete'),

    #! contactos
    path('contacto/', views.contact, name='contact'),
    #! about
    path('about/', views.about, name='about'),
    #! Mision y vision
    path('mision-vision/',views.mision_vision, name='mision_vision'),
]
