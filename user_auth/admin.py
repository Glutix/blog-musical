# user_auth/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Profile

# Configuración para mostrar Profile junto con User
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Perfiles'
    fk_name = 'user'

class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)

# Re-registrar el modelo User con la configuración personalizada
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Registrar Profile por separado también (opcional)
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_author', 'created_at')
    list_filter = ('is_author', 'created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Usuario', {
            'fields': ('user',)
        }),
        ('Información del Perfil', {
            'fields': ('avatar', 'bio', 'web_site', 'birth_date')
        }),
        ('Configuraciones', {
            'fields': ('is_author',)
        }),
        ('Fechas', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )