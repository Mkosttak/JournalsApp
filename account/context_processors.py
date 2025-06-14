from articles.models import Article

def user_context(request):
    context = {}
    if request.user.is_authenticated:
        # Admin için taslak makale sayısı
        if request.user.is_superuser:
            context['is_admin'] = True
            context['draft_articles_count'] = Article.objects.filter(isHome=False).count()
        
        # Editör için taslak makale sayısı
        if hasattr(request.user, 'author') and request.user.author.editor_article:
            context['is_editor'] = True
            context['editor_draft_articles_count'] = Article.objects.filter(isHome=False).count()
    
    return context 