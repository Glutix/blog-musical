# blog/apps.py
from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.utils.text import slugify  # <-- ¡Importamos slugify aquí!


def create_initial_data(sender, **kwargs):
    # Importamos los modelos con los nombres correctos
    from .models import Category, Tag, Article

    # --- Crear categorías y tags ---
    categories = [
        "Rock",
        "Pop",
        "Jazz",
        "Clásica",
        "Electrónica",
        "Hip Hop",
        "Reggae",
        "Country",
        "Blues",
        "Metal",
        "Indie",
        "Folk",
        "Soul",
        "R&B",
        "Funk",
    ]

    for name in categories:
        Category.objects.get_or_create(
            name=name, defaults={"description": f"Descripción para la categoría {name}"}
        )

    tags = [
        "Guitarras",
        "Batería",
        "Teclados",
        "Voz",
        "Bajo",
        "Letras",
        "Producción",
        "Conciertos",
        "Álbumes",
        "Éxitos",
        "Historia",
        "Instrumentos",
        "Tendencias",
        "Entrevistas",
        "Críticas",
    ]

    for name in tags:
        Tag.objects.get_or_create(name=name)

    # --- Crear artículos iniciales (solo si no existen) ---
    User = get_user_model()
    admin_user, created = User.objects.get_or_create(
        username="integrate", defaults={"is_staff": True, "is_superuser": True}
    )
    if created:
        admin_user.set_password("123456music")
        admin_user.save()

    all_categories = list(Category.objects.all())
    all_tags = list(Tag.objects.all())

    if not Article.objects.exists():
        for i in range(1, 11):
            title = f"Artículo de Prueba {i}"
            content = (
                f"Este es el contenido del Artículo de Prueba número {i}. "
                "Sirve para llenar la base de datos con contenido de ejemplo."
            )

            # Generar el slug único para cada artículo
            # Se usa slugify para convertir el título en un slug válido
            base_slug = slugify(title)
            slug = base_slug
            counter = 1
            while Article.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            # Ahora pasamos el slug al crear el artículo
            article = Article.objects.create(
                title=title,
                content=content,
                user=admin_user,
                slug=slug,  # <-- ¡Aquí está el cambio clave!
            )

            # Asignar categorías y tags al artículo
            article.category.add(*all_categories[:2])
            article.tags.add(*all_tags[:3])
            article.save()


class BlogConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "blog"

    def ready(self):
        post_migrate.connect(create_initial_data, sender=self)
