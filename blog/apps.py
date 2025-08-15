# blog/apps.py

from django.apps import AppConfig
from django.conf import settings
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.utils.text import slugify 
import os
import cloudinary
import cloudinary.uploader
import cloudinary.api
from glob import glob

# Esta función se ejecutará después de las migraciones para poblar la base de datos
@receiver(post_migrate, sender='blog')
def create_initial_data(sender, **kwargs):
    # Importamos los modelos con los nombres correctos
    from .models import Category, Tag, Article

    # --- Estructura para los datos iniciales de las categorías ---
    category_image_urls = {
        "Rock": "https://res.cloudinary.com/dt5xp6kba/image/upload/v1755195828/rock_tqsdzc.jpg",
        "Pop": "https://res.cloudinary.com/dt5xp6kba/image/upload/v1755195767/pop_yabbzn.jpg",
        "Trap": "https://res.cloudinary.com/dt5xp6kba/image/upload/v1755195763/trap_q6f1mt.jpg",
        "Jazz": "https://res.cloudinary.com/dt5xp6kba/image/upload/v1755195853/jazz_fkoysj.jpg",
        "Rap": "https://res.cloudinary.com/dt5xp6kba/image/upload/v1755195839/rap_vbctns.jpg",
        "Clásica": "https://res.cloudinary.com/dt5xp6kba/image/upload/v1755195873/cl%C3%A1sica_iiya9a.jpg",
        "Electrónica": "https://res.cloudinary.com/dt5xp6kba/image/upload/v1755195767/electr%C3%B3nica_ihnemd.jpg",
        "Hip Hop": "https://res.cloudinary.com/dt5xp6kba/image/upload/v1755195767/hiphop_pqm8mb.jpg",
        "Reggae": "https://res.cloudinary.com/dt5xp6kba/image/upload/v1755195750/reggae_iezjh8.jpg",
        "Country": "https://res.cloudinary.com/dt5xp6kba/image/upload/v1755195870/country_b2efud.jpg",
        "Blues": "https://res.cloudinary.com/dt5xp6kba/image/upload/v1755195879/blues_nahvbe.jpg",
        "Metal": "https://res.cloudinary.com/dt5xp6kba/image/upload/v1755195847/metal_ck92lz.jpg",
        "Indie": "https://res.cloudinary.com/dt5xp6kba/image/upload/v1755195766/indie_sx7117.jpg",
        "Folk": "https://res.cloudinary.com/dt5xp6kba/image/upload/v1755195765/folk_v3d4sd.jpg",
        "Funk": "https://res.cloudinary.com/dt5xp6kba/image/upload/v1755195764/funk_cfossq.jpg",
    }

    # --- Estructura para los datos iniciales de los tags ---
    tags_list = [
        "Guitarras", "Batería", "Teclados", "Voz", "Bajo", "Letras", "Producción",
        "Conciertos", "Álbumes", "Éxitos", "Historia", "Instrumentos", "Tendencias",
        "Entrevistas", "Críticas",
    ]

    # --- Estructura para los datos de los 10 artículos editables con descripciones más largas ---
    # NOTA: Reemplaza las URL de ejemplo con los enlaces de tus imágenes de Cloudinary.
    # La URL completa de la imagen se guardará en el campo 'featured_image'.
    articles_data = [
        {
            "title": "La Historia del Rock",
            "content": (
                "Un viaje fascinante a través de los orígenes y la evolución del rock, "
                "desde sus raíces en el blues y el country hasta los sonidos eléctricos y rebeldes "
                "que lo definieron. Exploramos a los pioneros como Elvis Presley y Chuck Berry, "
                "el impacto de bandas como The Beatles y Led Zeppelin, y la diversificación del "
                "género en el punk, el metal y el rock alternativo. Un recorrido por los momentos "
                "clave que hicieron del rock la banda sonora de varias generaciones. Su influencia "
                "es innegable en la cultura, la moda y la actitud de millones de personas en todo el mundo."
            ),
            "image_url": "https://res.cloudinary.com/dt5xp6kba/image/upload/v1755197098/articulo-rock_wlttlq.jpg", 
            "categories": ["Rock"],
            "tags": ["Guitarras", "Batería", "Historia"],
        },
        {
            "title": "Los Éxitos Inolvidables del Pop",
            "content": (
                "Analizamos las canciones que no solo definieron el género pop, sino que también "
                "se convirtieron en himnos culturales. Desde la era dorada del pop de los 80 con "
                "Madonna y Michael Jackson, hasta las superestrellas modernas como Taylor Swift "
                "y Beyoncé. Este artículo examina las estructuras musicales pegadizas, las "
                "producciones innovadoras y el impacto comercial que hacen que una canción sea un "
                "éxito mundial. Es un homenaje a la música que nos hace bailar, cantar y sentir."
            ),
            "image_url": "https://res.cloudinary.com/dt5xp6kba/image/upload/v1755197077/articulo-pop_ehl28b.jpg",
            "categories": ["Pop"],
            "tags": ["Éxitos", "Producción", "Voz"],
        },
        {
            "title": "El Fenómeno del Trap",
            "content": (
                "Exploramos cómo el trap, un subgénero del hip hop, pasó de ser un sonido underground "
                "en Atlanta a dominar las listas de popularidad a nivel global. Analizamos sus ritmos "
                "distintivos, el uso de sintetizadores y la lírica enfocada en la vida en la calle, "
                "el éxito y los desafíos. Además, revisamos su impacto en la moda, la cultura urbana y "
                "su evolución en diferentes países. Artistas como Bad Bunny y Travis Scott han llevado "
                "este género a un nuevo nivel de masividad y reconocimiento internacional."
            ),
            "image_url": "https://res.cloudinary.com/dt5xp6kba/image/upload/v1755197100/articulo-trap_dzzkkr.jpg",
            "categories": ["Trap", "Hip Hop"],
            "tags": ["Producción", "Tendencias", "Letras"],
        },
        {
            "title": "El Jazz y sus Leyendas",
            "content": (
                "Un recorrido por la vida y obra de los músicos que hicieron del jazz un género atemporal "
                "y sofisticado. Desde los clubes de Nueva Orleans hasta los grandes salones de Nueva York, "
                "conoceremos a figuras icónicas como Louis Armstrong, Miles Davis, y Ella Fitzgerald. "
                "Analizamos la improvisación, las estructuras complejas y la profunda expresividad que "
                "caracterizan a este género. El jazz es más que música; es una conversación entre "
                "instrumentos que representa la libertad artística y la innovación constante."
            ),
            "image_url": "https://res.cloudinary.com/dt5xp6kba/image/upload/v1755197124/articulo-jazz_vl710n.jpg",
            "categories": ["Jazz"],
            "tags": ["Instrumentos", "Historia", "Entrevistas"],
        },
        {
            "title": "La Revolución del Rap",
            "content": (
                "Desde las block parties del Bronx hasta la actualidad, el rap se ha consolidado como "
                "una de las formas de expresión más influyentes del siglo XXI. Exploramos su nacimiento "
                "como una manifestación cultural, su evolución a través de la edad de oro con artistas "
                "como Tupac y Notorious B.I.G., y su impacto en la política, la sociedad y el arte. "
                "El rap es poesía urbana, protesta social y un reflejo de la vida contemporánea que "
                "sigue redefiniendo los límites de la música."
            ),
            "image_url": "https://res.cloudinary.com/dt5xp6kba/image/upload/v1755197078/articulo-rap_mu0jkr.jpg",
            "categories": ["Rap", "Hip Hop"],
            "tags": ["Letras", "Historia", "Éxitos"],
        },
        {
            "title": "Los Secretos de la Música Clásica",
            "content": (
                "Una guía exhaustiva para principiantes que busca desmitificar la música clásica. "
                "Aprenderás sobre los compositores más grandes de la historia, desde Bach y Mozart "
                "hasta Beethoven y Stravinsky. Desglosamos los conceptos clave como sinfonías, "
                "sonatas y óperas, y te mostramos cómo escuchar y apreciar las complejidades y "
                "belleza de este género. La música clásica es un tesoro cultural que ha resistido "
                "el paso del tiempo, y aquí te ayudamos a descubrir su magia."
            ),
            "image_url": "https://res.cloudinary.com/dt5xp6kba/image/upload/v1755197117/articulo-clasica_jssu80.jpg",
            "categories": ["Clásica"],
            "tags": ["Instrumentos", "Historia"],
        },
        {
            "title": "La Vanguardia Electrónica",
            "content": (
                "El surgimiento de la música electrónica fue una revolución sonora que transformó "
                "la industria. Este artículo explora sus subgéneros, desde el techno y el house "
                "hasta el trance y el dubstep. Analizamos el papel de los sintetizadores y las "
                "cajas de ritmos en su creación, y su influencia en la música popular y de club "
                "en todo el mundo. Te llevamos a un viaje a través de los festivales, los DJs "
                "legendarios y los innovadores que construyeron un nuevo universo musical."
            ),
            "image_url": "https://res.cloudinary.com/dt5xp6kba/image/upload/v1755197119/articulo-electronica_voxqsu.jpg",
            "categories": ["Electrónica"],
            "tags": ["Producción", "Tendencias", "Álbumes"],
        },
        {
            "title": "El Impacto del Hip Hop",
            "content": (
                "Más que un género musical, el hip hop es una cultura que transformó el arte, "
                "la moda y la danza en todo el mundo. Exploramos sus cuatro elementos principales: "
                "el MCing, el DJing, el graffiti y el breakdance. Este artículo profundiza en "
                "cómo el hip hop se convirtió en una voz poderosa para las comunidades marginadas "
                "y cómo artistas como Run-DMC y Public Enemy cambiaron el panorama musical y social. "
                "Su legado sigue vivo y evolucionando en cada rincón del planeta."
            ),
            "image_url": "https://res.cloudinary.com/dt5xp6kba/image/upload/v1755197122/articulo-hiphop_a1wqfd.jpg",
            "categories": ["Hip Hop"],
            "tags": ["Letras", "Historia", "Conciertos"],
        },
        {
            "title": "La Vibración del Reggae",
            "content": (
                "Descubre la historia, los mensajes de paz y el ritmo contagioso del reggae, "
                "nacido en Jamaica. Exploramos sus raíces en el ska y el rocksteady, y la "
                "filosofía rastafari que lo inspira. Conocemos a sus figuras más icónicas, "
                "con Bob Marley a la cabeza, quien llevó este mensaje de unidad y conciencia "
                "al mundo entero. El reggae es un género con alma, que te invita a reflexionar "
                "y a moverte al ritmo de sus vibraciones únicas."
            ),
            "image_url": "https://res.cloudinary.com/dt5xp6kba/image/upload/v1755197097/articulo-reggae_ixpbkf.jpg",
            "categories": ["Reggae"],
            "tags": ["Bajo", "Letras", "Historia"],
        },
        {
            "title": "El Alma del Blues",
            "content": (
                "Un tributo a los pioneros del blues, la música que nació del dolor y la esperanza "
                "en las comunidades afroamericanas del sur de Estados Unidos. Este género sentó "
                "las bases para el rock and roll, el jazz y gran parte de la música moderna. "
                "Exploramos las vidas de leyendas como B.B. King y Muddy Waters, y la estructura "
                "de 12 compases que se convirtió en su firma. El blues es un género lleno de "
                "emoción y autenticidad que cuenta historias de lucha y perseverancia."
            ),
            "image_url": "https://res.cloudinary.com/dt5xp6kba/image/upload/v1755197313/articulo-blue_h9yvpu.jpg",
            "categories": ["Blues"],
            "tags": ["Guitarras", "Voz", "Historia"],
        },
    ]

    # --- Crear categorías y tags ---
    for name, image_url in category_image_urls.items():
        Category.objects.get_or_create(
            name=name, defaults={"description": f"Descripción para la categoría {name}", "image": image_url}
        )

    for name in tags_list:
        Tag.objects.get_or_create(name=name)

    # --- Crear artículos iniciales (solo si no existen) ---
    User = get_user_model()
    admin_user, created = User.objects.get_or_create(
        username="integrate", defaults={"is_staff": True, "is_superuser": True}
    )
    if created:
        admin_user.set_password("123456music")
        admin_user.save()

    if not Article.objects.exists():
        for article_data in articles_data:
            title = article_data["title"]
            content = article_data["content"]
            image_url = article_data["image_url"]

            # Generar el slug único para cada artículo
            base_slug = slugify(title)
            slug = base_slug
            counter = 1
            while Article.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            # Creamos el artículo con los campos del modelo que proporcionaste
            article = Article.objects.create(
                title=title, 
                content=content, 
                user=admin_user, 
                slug=slug,
                featured_image=image_url # Asignamos la URL de la imagen que el usuario pegará manualmente
            )

            # Asignar categorías y tags al artículo (ManyToManyField)
            for cat_name in article_data["categories"]:
                category = Category.objects.get(name=cat_name)
                article.category.add(category)
            
            for tag_name in article_data["tags"]:
                tag = Tag.objects.get(name=tag_name)
                article.tags.add(tag)
            
            article.save()

class BlogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blog'

    def ready(self):
        post_migrate.connect(create_initial_data, sender=self)
