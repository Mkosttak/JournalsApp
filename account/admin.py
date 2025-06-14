from django.contrib import admin
from .models import Author


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'is_approved', 'editor_article', 'articles_count', 'created_at','updated_at')
    list_filter = ('is_approved', 'editor_article')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    actions = ['approve_authors', 'unapprove_authors', 'enable_editor_article', 'disable_editor_article']

    def full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"

    def articles_count(self, obj):
        return obj.user.article_set.count()

    def approve_authors(self, request, queryset):
        queryset.update(is_approved=True)

    approve_authors.short_description = "Seçilen yazarları onayla"

    def unapprove_authors(self, request, queryset):
        queryset.update(is_approved=False)

    unapprove_authors.short_description = "Seçilen yazarların onayını kaldır"

    def enable_editor_article(self, request, queryset):
        queryset.update(editor_article=True)

    enable_editor_article.short_description = "Seçilen yazarlara editör yetkisi ver"

    def disable_editor_article(self, request, queryset):
        queryset.update(editor_article=False)

    disable_editor_article.short_description = "Seçilen yazarların editör yetkisini kaldır"