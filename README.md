# 🎵 Blog Musical

Blog Musical es una plataforma desarrollada en Django que permite a los usuarios explorar, compartir y valorar artículos relacionados con la música. Incluye funcionalidades como publicaciones, comentarios, likes, visitas, valoraciones, perfiles de usuario y sistema de etiquetas.

## 🚀 Tecnologías

- Python
- Django
- MySQL
- HTML, CSS, JavaScript
- Git & GitHub

## 📁 Estructura del Proyecto

```bash
blog-musical/
│
├── config/             # Configuraciones de Django
├── core/               # Lógica principal del blog (artículos, comentarios, etc.)
├── users/              # Gestión de usuarios y perfiles
├── static/             # Archivos estáticos
├── templates/          # Templates HTML
├── .env                # Variables de entorno
├── requirements.txt    # Dependencias
└── README.md
```

## ⚙️ Configuración Inicial

1. Crear entorno virtual:

```bash
python -m venv env
```

2. Activar entorno virtual:

- Windows:
```bash
.\env\Scripts\activate
```

- Linux/Mac:
```bash
source env/bin/activate
```

3. Instalar dependencias:

```bash
pip install -r requirements.txt
```

4. Crear archivo `.env`:

```env
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
SECRET_KEY=tu_clave_secreta

DB_NAME=blog-musical
DB_USER=root
DB_PASSWORD=tu_password
DB_HOST=localhost
DB_PORT=3306
```

5. Migraciones y servidor:

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

## 🤝 Colaboradores

- [Ferreyra Ricardo](https://github.com/Glutix)
- [Benitez Cluadia](https://github.com/ClauBenitez)
- [Flores Mariana](https://github.com/Glutix)
- [Vargas Alejandro](https://github.com/dether)

## 📌 Estado del proyecto

En desarrollo 🛠️
