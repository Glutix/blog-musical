# blog/apps.py
from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth import get_user_model

def create_initial_data(sender, **kwargs):
    # ¡Importamos los modelos con los nombres correctos!
    from .models import Category, Tag, Article

    # --- Crear categorías y tags ---
    categories = [
        "Rock", "Pop", "Jazz", "Clásica", "Electrónica",
        "Hip Hop", "Reggae", "Country", "Blues", "Metal",
        "Indie", "Folk", "Soul", "R&B", "Funk",
    ]
    
    for name in categories:
        Category.objects.get_or_create(name=name)
    
    tags = [
        "Guitarras", "Batería", "Teclados", "Voz", "Bajo",
        "Letras", "Producción", "Conciertos", "Álbumes",
        "Éxitos", "Historia", "Instrumentos", "Tendencias",
        "Entrevistas", "Críticas",
    ]
    
    for name in tags:
        Tag.objects.get_or_create(name=name)

    # --- Crear artículos iniciales (solo si no existen) ---
    # Primero, obtenemos o creamos un usuario para ser el autor
    User = get_user_model()
    # Se crea el superusuario 'dether' con la contraseña 'asd123'
    # La contraseña se establece correctamente después de la creación del usuario.
    admin_user, created = User.objects.get_or_create(username='dether', defaults={'is_staff': True, 'is_superuser': True})
    if created:
        admin_user.set_password('asd123')
        admin_user.save()

    # Obtenemos las categorías y tags que acabamos de crear
    all_categories = list(Category.objects.all())
    all_tags = list(Tag.objects.all())

    # Creamos 10 artículos si no hay ninguno creado
    if not Article.objects.exists():
        for i in range(1, 11):
            title = f"Artículo de Prueba {i}"
            content = (
                f"Este es el contenido del Artículo de Prueba número {i}. "
                "Sirve para llenar la base de datos con contenido de ejemplo."
            )
            
            # Verificamos si el artículo existe antes de crearlo
            if not Article.objects.filter(title=title).exists():
                article = Article.objects.create(
                    title=title,
                    content=content,
                    # El campo de autor es 'user', no 'author'
                    user=admin_user
                    # El campo 'is_published' no existe en el modelo, por lo que se elimina
                )
                
                # Asignar categorías y tags al artículo
                article.category.add(*all_categories[:2])  # Asigna las primeras 2 categorías
                article.tags.add(*all_tags[:3])            # Asigna los primeros 3 tags
                article.save()


class BlogConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "blog"

    def ready(self):
        # Conecta la función a la señal `post_migrate`
        post_migrate.connect(create_initial_data, sender=self)

