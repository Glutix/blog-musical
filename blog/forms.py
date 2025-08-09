from django import forms
from .models import Article, Category, Tag

class ArticleForm(forms.ModelForm):
    """
    Formulario para crear y editar artículos
    """
    
    class Meta:
        model = Article
        fields = ['title', 'content', 'featured_image', 'category', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingresa el título del artículo...',
                'maxlength': 200
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': 'Escribe el contenido del artículo...'
            }),
            'featured_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'category': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            }),
            'tags': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'title': 'Título',
            'content': 'Contenido',
            'featured_image': 'Imagen destacada',
            'category': 'Categorías',
            'tags': 'Etiquetas',
        }
        help_texts = {
            'title': 'Máximo 200 caracteres',
            'content': 'Puedes usar Markdown para formatear el texto',
            'featured_image': 'Imagen opcional para el artículo (JPG, PNG, GIF)',
            'category': 'Selecciona una o más categorías',
            'tags': 'Selecciona las etiquetas relevantes',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Hacer que las categorías y tags sean opcionales
        self.fields['category'].required = False
        self.fields['tags'].required = False
        self.fields['featured_image'].required = False
        
        # Personalizar querysets si es necesario
        self.fields['category'].queryset = Category.objects.all()
        self.fields['tags'].queryset = Tag.objects.all()

    def clean_title(self):
        """
        Validación personalizada para el título
        """
        title = self.cleaned_data.get('title')
        if title:
            title = title.strip()
            if len(title) < 5:
                raise forms.ValidationError('El título debe tener al menos 5 caracteres.')
        return title

    def clean_content(self):
        """
        Validación personalizada para el contenido
        """
        content = self.cleaned_data.get('content')
        if content:
            content = content.strip()
            if len(content) < 50:
                raise forms.ValidationError('El contenido debe tener al menos 50 caracteres.')
        return content