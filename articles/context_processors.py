from articles.models import Article
from pages.models import Contact

def unread_admin_notes_count(request):
    if request.user.is_authenticated:
        count = Article.objects.filter(author=request.user, is_admin_note_read_by_author=False).count()
        return {'unread_admin_notes_count': count}
    return {'unread_admin_notes_count': 0}

def admin_notifications(request):
    if request.user.is_authenticated and request.user.is_superuser:
        unread_messages = Contact.objects.filter(is_answered=False).count()
        draft_articles = Article.objects.filter(isHome=False).count()
        return {
            'unread_messages_count': unread_messages,
            'draft_articles_count': draft_articles
        }
    return {
        'unread_messages_count': 0,
        'draft_articles_count': 0
    } 