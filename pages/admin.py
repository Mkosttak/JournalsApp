from django.contrib import admin
from .models import Contact, Subscriber

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at', 'is_answered')
    list_filter = ('is_answered', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('name', 'email', 'subject', 'message', 'created_at')
    list_per_page = 20

    def has_add_permission(self, request):
        # Admin panelinden yeni mesaj eklenmesini engelle
        return False

class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'subscribed_at')
    search_fields = ('email',)
    list_filter = ('subscribed_at',)

admin.site.register(Subscriber, SubscriberAdmin)