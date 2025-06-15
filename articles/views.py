from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ArticleCreateForm, ArticleEditForm, UserArticleEditForm
from .models import Article, Category
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q, Count
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.text import slugify
from django.db import transaction
import json
from account.models import Author

# Helper function to check if user is superuser or has editor_article permission
def is_editor_or_superuser(user):
    if user.is_superuser:
        return True
    return hasattr(user, 'author') and user.author.editor_article

# Giriş sayfası (ana sayfa)
def index(request):
    query = request.GET.get("q", "").strip()
    makaleler = Article.objects.filter(isHome=True)
    
    if query != "":
        makaleler = makaleler.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(author__first_name__icontains=query) |
            Q(author__last_name__icontains=query) |
            Q(keywords__icontains=query)
        )

    # Her makale için anahtar kelimeleri listeye dönüştür
    for article in makaleler:
        if article.keywords:
            article.keyword_list = [k.strip() for k in article.keywords.split(',') if k.strip()]
        else:
            article.keyword_list = []

    kategoriler = Category.objects.all()
    return render(request, 'articles/index.html', {
        'categories': kategoriler,
        'articles': makaleler,
        'query': query
    })

# Arama fonksiyonu
def search(request):
    if "q" in request.GET and request.GET["q"] != "":
        q = request.GET["q"]
        articles = Article.objects.filter(isHome=True, title__icontains=q).order_by("date")
        categories = Category.objects.all()
    else:
        return redirect("/makale")

    return render(request, 'articles/search.html', {
        'categories': categories,
        'articles': articles,
    })

# Sadece admin girebilir (bu fonksiyon artık kullanılmayacak, is_editor_or_superuser kullanılacak)
def isAdmin(user):
    return user.is_superuser

@login_required()
def article_create(request):
    if request.method == "POST":
        form = ArticleCreateForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            form.save_m2m()
            messages.success(request, "Makale başarıyla oluşturuldu ve yayınlanmak üzere incelenmeyi bekliyor.")
            return redirect('account:my_articles')
        else:
            return render(request, 'articles/article-create.html', {"form": form})
    else:
        form = ArticleCreateForm()
    return render(request, 'articles/article-create.html', {"form": form})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def article_list(request):
    query = request.GET.get("q", "").strip()
    articles = Article.objects.all().select_related('author').order_by('isHome', '-created_at')

    if query:
        articles = articles.filter(
            Q(title__icontains=query) |
            Q(author__first_name__icontains=query) |
            Q(author__last_name__icontains=query) |
            Q(keywords__icontains=query)
        ).distinct()

    for article in articles:
        if article.keywords:
            article.keyword_list = [k.strip() for k in article.keywords.split(',') if k.strip()]
        else:
            article.keyword_list = []

    return render(request, 'articles/article-list.html', {
        'articles': articles,
        'query': query
    })

@login_required
def article_edit(request, id):
    try:
        article = get_object_or_404(Article, pk=id)
    except ValueError:
        article = get_object_or_404(Article, slug=id)

    # Admin veya editör yetkisi olanlar tüm makaleleri düzenleyebilir
    if request.user.is_superuser:
        form_class = ArticleEditForm
        template = 'articles/article-edit-admin.html'
    elif hasattr(request.user, 'author') and request.user.author.editor_article:
        if request.user == article.author: # Editör kendi makalesini düzenliyor
            form_class = UserArticleEditForm
            template = 'articles/article-edit.html'
        else: # Editör başkasının makalesini düzenliyor
            form_class = ArticleEditForm
            template = 'articles/article-edit-admin.html'
    elif request.user == article.author:
        # Normal kullanıcı kendi makalesini düzenliyor
        form_class = UserArticleEditForm
        template = 'articles/article-edit.html'
    else:
        raise PermissionDenied()

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=article)
        if form.is_valid():
            print("Form geçerli!")
            print("Formun changed_data:", form.changed_data)
            print("Formun cleaned_data['file']:", form.cleaned_data.get('file'))
            print("Request.FILES:", request.FILES)

            # Formdan güncellenmiş nesneyi al (henüz kaydetme)
            updated_article = form.save(commit=False)
            
            # isHome ve admin_note ile ilgili özel mantıkları buraya ekle
            # Eğer normal bir kullanıcı kendi makalesini düzenliyorsa ve makale yayınlanmışsa,
            # tekrar onaya düşürmek için isHome'u False yap.
            if request.user == article.author and article.isHome and 'isHome' not in form.changed_data:
                updated_article.isHome = False
                messages.info(request, "Makaleniz güncellendi. Yeni değişiklikler editör tarafından incelendikten sonra tekrar yayınlanacaktır.")
            
            # admin_note'un orijinal halini, veritabanından çekerek al. Bu, güncel form verilerini etkilemez.
            original_admin_note = Article.objects.get(pk=article.pk).admin_note

            # Eğer süperuser veya editör notu güncelliyorsa, okunmadı olarak işaretle
            if request.user.is_superuser or (hasattr(request.user, 'author') and request.user.author.editor_article):
                if updated_article.admin_note != original_admin_note:
                    updated_article.is_admin_note_read_by_author = False
            
            # Eğer makalenin yazarı kendi makalesini düzenliyorsa, notu okundu olarak işaretle
            if request.user == article.author:
                updated_article.is_admin_note_read_by_author = True

            # Tüm değişiklikleri veritabanına kaydet (dosya dahil)
            updated_article.save()
            form.save_m2m()

            messages.success(request, "Makale başarıyla güncellendi.")

            if request.user.is_superuser:
                return redirect('articles:article_list')
            elif hasattr(request.user, 'author') and request.user.author.editor_article:
                return redirect('account:editor_articles')
            else:
                return redirect('account:my_articles')
        else:
            # Form geçerli değilse hataları kullanıcıya göster
            # for field, errors in form.errors.items():
            #     for error in errors:
            #         messages.error(request, f"Lütfen {field} alanını kontrol edin: {error}")
            return render(request, template, {"form": form})
    else:
        form = form_class(instance=article)

    return render(request, template, {"form": form})

@login_required
@csrf_protect
def article_delete(request, id):
    try:
        article = get_object_or_404(Article, pk=id)
    except ValueError:
        article = get_object_or_404(Article, slug=id)

    # Sadece superuser veya makalenin yazarı silebilir
    if not (request.user.is_superuser or request.user == article.author):
        raise PermissionDenied("Bu makaleyi silme yetkiniz bulunmamaktadır.")

    if request.method == "POST":
        article.delete()
        messages.success(request, "Makale başarıyla silindi.")
        # Kullanıcı tipine göre yönlendirme yap
        if request.user.is_superuser:
            return redirect('articles:article_list')
        else:
            return redirect('account:my_articles')

    return render(request, 'articles/article-delete.html', {'article': article})

# Dosya yükleme (örnek amaçlı)
def upload(request):
    pass
    # if request.method == "POST":
    #     form = UploadForm(request.POST, request.FILES)
    #     if form.is_valid():
    #         model = UploadModel(image=request.FILES["image"])
    #         model.save()
    #         return render(request, 'articles/success.html')
    # else:
    #     form = UploadForm()
    # return render(request, 'articles/upload.html', {"form": form})

# Makale detay sayfası
def details(request, slug):
    article = get_object_or_404(Article, slug=slug)
    
    if article.keywords:
        article.keyword_list = [k.strip() for k in article.keywords.split(',') if k.strip()]
    else:
        article.keyword_list = []

    context = {
        'article': article
    }
    return render(request, 'articles/details.html', context)

# Kategoriye göre filtrelenmiş makaleler
def getArticlesByCategory(request, slug):
    query = request.GET.get("q", "").strip()
    articles = Article.objects.filter(categories__slug=slug, isHome=True)

    if query:
        articles = articles.filter(
            Q(title__icontains=query) |
            Q(author__first_name__icontains=query) |
            Q(author__last_name__icontains=query) |
            Q(keywords__icontains=query)
        ).distinct()
    
    for article in articles:
        if article.keywords:
            article.keyword_list = [k.strip() for k in article.keywords.split(',') if k.strip()]
        else:
            article.keyword_list = []

    categories = Category.objects.all()

    paginator = Paginator(articles, 2)
    page = request.GET.get('page', 1)
    page_obj = paginator.page(page)

    return render(request, 'articles/list.html', {
        'categories': categories,
        'page_obj': page_obj,
        'seciliKategori': slug,
        'query': query,
    })

@login_required
def profile_edit(request):
    # ProfileEditForm ve Profile importlarını kaldırıyorum, çünkü artık bu form ve model burada kullanılmıyor.
    pass

@login_required
@user_passes_test(lambda u: u.is_superuser)
@require_POST
def create_category_ajax(request):
    category_name = request.POST.get('name', '').strip()
    if not category_name:
        return JsonResponse({'error': 'Kategori adı boş olamaz.'}, status=400)

    if Category.objects.filter(name__iexact=category_name).exists():
        return JsonResponse({'error': 'Bu kategori zaten mevcut.'}, status=400)

    try:
        new_category = Category.objects.create(name=category_name, slug=slugify(category_name))
        return JsonResponse({'id': new_category.id, 'name': new_category.name})
    except Exception as e:
        return JsonResponse({'error': f'Kategori oluşturulurken bir hata oluştu: {str(e)}'}, status=500)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_categories(request):
    categories = Category.objects.annotate(article_count=Count('article')).order_by('-order')
    
    query = request.GET.get("q", "").strip()
    
    return render(request, 'articles/admin-categories.html', {
        'categories': categories,
        'query': query
    })

@login_required
@user_passes_test(lambda u: u.is_superuser)
@require_POST
def category_delete(request, id):
    category = get_object_or_404(Category, pk=id)
    category.delete()
    messages.success(request, f'"{category.name}" kategorisi başarıyla silindi.')
    return redirect('articles:admin_categories')

@login_required
@require_POST
@csrf_protect
def mark_comment_as_read(request, comment_id):
    try:
        comment = get_object_or_404(Comment, pk=comment_id)
        # Yorumu sadece makalenin yazarı okundu olarak işaretleyebilir
        if request.user != comment.article.author:
            return JsonResponse({'success': False, 'error': 'Bu yorumu okundu olarak işaretleme yetkiniz yok.'}, status=403)
        
        data = json.loads(request.body)
        is_read = data.get('is_read', False)
        
        comment.is_read = is_read
        comment.save()
        return JsonResponse({'success': True})
    except Comment.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Yorum bulunamadı.'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Geçersiz JSON.'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)