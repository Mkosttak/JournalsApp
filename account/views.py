from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q, Count
from account.forms import LoginUserForm, NewUserForm, UserPasswordChangeForm, AuthorProfileForm, UserProfileForm, UserUpdateForm
from articles.models import Article
from account.models import Author
from django.http import Http404
from django.views.decorators.http import require_POST


def user_login(request):
    if request.user.is_authenticated and "next" in request.GET:
        return render(request, 'account/login.html', {"error": "Yetkiniz Yok!"})
    if request.method == "POST":
        form = LoginUserForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                nextUrl = request.GET.get('next', None)
                return redirect(nextUrl if nextUrl else 'pages:index')
            else:
                return render(request, 'account/login.html', {"form": form})
        else:
            return render(request, 'account/login.html', {"form": form})
    else:
        form = LoginUserForm()
        return render(request, 'account/login.html', {"form": form})

def user_register(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            Author.objects.create(user=user)
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.add_message(request, messages.SUCCESS, 'Başarılı bir şekilde kayıt oldunuz! Profilinizi düzenleyebilirsiniz.')
            return redirect('account:profile')
        else:
            return render(request, 'account/register.html', {"form": form})
    else:
        form = NewUserForm()
        return render(request, 'account/register.html', {"form": form})

@login_required
def change_password(request):
    if request.method == "POST":
        form = UserPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Parolanız Güncellendi!')
            return redirect('account:change_password')
        else:
            messages.error(request, 'Tekrar Deneyiniz!')
    else:
        form = UserPasswordChangeForm(request.user)
    return render(request, 'account/change-password.html', {"form": form})

def user_logout(request):
    messages.add_message(request, messages.SUCCESS, 'Çıkış Başarılı!')
    logout(request)
    return redirect('pages:index')

@login_required
def profile(request):
    author, created = Author.objects.get_or_create(user=request.user)
    # If the author was just created or doesn't have a profile image, set the default
    if created or not author.profile_image:
        author.profile_image = "author_profiles/default.png"
        author.save()

    total_articles = Article.objects.filter(author=request.user).count()
    published_articles = Article.objects.filter(author=request.user, isHome=True).count()
    pending_articles = Article.objects.filter(author=request.user, isHome=False).count()
    recent_articles = Article.objects.filter(author=request.user).order_by('-created_at')[:5]
    context = {
        'author': author,
        'total_articles': total_articles,
        'published_articles': published_articles,
        'pending_articles': pending_articles,
        'recent_articles': recent_articles,
    }
    return render(request, 'account/profile.html', context)

@login_required
def profile_edit(request):
    author = Author.objects.get(user=request.user)
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        author_form = AuthorProfileForm(request.POST, request.FILES, instance=author, user=request.user)
        if user_form.is_valid() and author_form.is_valid():
            user_form.save()

            # Handle resume clearing
            if author_form.cleaned_data.get('clear_resume'):
                author.resume = None

            # Handle profile image clearing
            if author_form.cleaned_data.get('clear_profile_image'):
                author.profile_image = None

            # Save the author instance, which will save new files or set fields to None as appropriate
            author.save()
            # The author_form.save() call is no longer needed here for file fields,
            # as we explicitly handle resume and profile_image. 
            # If there were other fields in AuthorProfileForm not directly handled,
            # author_form.save() would be appropriate, but with this structure,
            # direct saving of `author` instance is cleaner after modifying fields directly.
            # If `author_form.save()` is called after setting `author.resume = None`
            # and `author.profile_image = None`, it might try to re-save previous values
            # if the form still holds them from `instance=author`.
            # Given `AuthorProfileForm` only has `profile_image`, `bio`, `resume`, `is_approved`
            # and we handle `profile_image` and `resume` explicitly here, 
            # `author.save()` should be sufficient to persist the changes to these fields.

            messages.success(request, 'Profiliniz başarıyla güncellendi.')
            return redirect('account:profile')
        else:
            # Display form errors if validation fails
            if not user_form.is_valid():
                for field, errors in user_form.errors.items():
                    for error in errors:
                        messages.error(request, f"Kullanıcı Bilgileri - {field}: {error}")
                for error in user_form.non_field_errors():
                    messages.error(request, f"Kullanıcı Bilgileri: {error}")

            if not author_form.is_valid():
                for field, errors in author_form.errors.items():
                    for error in errors:
                        messages.error(request, f"Yazar Bilgileri - {field}: {error}")
                for error in author_form.non_field_errors():
                    messages.error(request, f"Yazar Bilgileri: {error}")

    else:
        user_form = UserUpdateForm(instance=request.user)
        author_form = AuthorProfileForm(instance=author, user=request.user)
    context = {
        'user_form': user_form,
        'author_form': author_form,
        'author': author,
        'user': request.user
    }
    return render(request, 'account/profile_edit.html', context)

@login_required
def my_articles(request):
    query = request.GET.get("q", "").strip()
    articles = Article.objects.filter(author=request.user)

    if query:
        articles = articles.filter(
            Q(title__icontains=query) |
            Q(author__first_name__icontains=query) |
            Q(author__last_name__icontains=query) |
            Q(keywords__icontains=query)
        ).distinct()

    # Her makale için anahtar kelimeleri listeye dönüştür
    for article in articles:
        if article.keywords:
            article.keyword_list = [k.strip() for k in article.keywords.split(',') if k.strip()]
        else:
            article.keyword_list = []

    total_articles = articles.count()
    approved_articles = articles.filter(isHome=True).count()
    pending_articles = articles.filter(isHome=False).count()
    
    context = {
        'articles': articles,
        'total_articles': total_articles,
        'approved_articles': approved_articles,
        'pending_articles': pending_articles,
        'query': query
    }
    return render(request, 'account/my-articles.html', context)

def authors_list(request):
    query = request.GET.get("q", "").strip()
    if query != "":
        authors = Author.objects.filter(
            Q(is_approved=True),
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(user__email__icontains=query)
        )
    else:
        authors = Author.objects.filter(is_approved=True)

    return render(request, 'account/authors-list.html', {
        'authors': authors,
        'query': query
    })

def author_detail(request, author_id):
    author = get_object_or_404(Author, id=author_id)
    articles = Article.objects.filter(author=author.user, isHome=True)
    return render(request, 'account/author-detail.html', {'author': author, 'articles': articles})

@login_required
def profile_view(request):
    user = request.user
    author, created = Author.objects.get_or_create(user=user)
    if request.method == "POST":
        user_form = UserProfileForm(request.POST, instance=user)
        author_form = AuthorProfileForm(request.POST, request.FILES, instance=author, user=user)
        if user_form.is_valid() and author_form.is_valid():
            user_form.save()
            author_form.save()
            messages.success(request, "Profil başarıyla güncellendi.")
            return redirect('account:profile')
        else:
            messages.error(request, "Lütfen formdaki hataları düzeltin.")
    else:
        user_form = UserProfileForm(instance=user)
        author_form = AuthorProfileForm(instance=author, user=user)
    user_articles = Article.objects.filter(author=user)
    return render(request, 'account/profile.html', {
        'user_form': user_form,
        'author_form': author_form,
        'articles': user_articles,
        'author': author,
    })

@user_passes_test(lambda u: u.is_superuser)
def admin_authors(request):
    authors = Author.objects.filter(user__is_superuser=False).annotate(article_count=Count('user__article')).order_by('-editor_article', '-is_approved', 'created_at')
    return render(request, 'account/admin-authors.html', {'authors': authors})

@login_required
@user_passes_test(lambda u: u.is_superuser)
@require_POST
def author_delete(request, id):
    author = get_object_or_404(Author, pk=id)
    # Also delete the associated User object
    user = author.user
    author.delete()
    user.delete() # This will delete the user and cascade to related models if set up
    messages.success(request, f'"{user.username}" kullanıcısı ve yazarı başarıyla silindi.')
    return redirect('account:admin_authors')

@login_required
@user_passes_test(lambda u: u.is_superuser)
def authors_edit(request, author_id):
    author = get_object_or_404(Author, id=author_id)
    user_form = UserProfileForm(request.POST or None, instance=author.user)
    author_form = AuthorProfileForm(request.POST or None, request.FILES or None, instance=author)
    if request.method == 'POST':
        if user_form.is_valid() and author_form.is_valid():
            user_form.save()
            # Handle resume clearing
            if author_form.cleaned_data.get('clear_resume'):
                author.resume = None
            # Handle profile image clearing
            if author_form.cleaned_data.get('clear_profile_image'):
                author.profile_image = None
            # Save author form data
            author_form.save()
            messages.success(request, 'Editör bilgileri başarıyla güncellendi.')
            return redirect('account:admin_authors')
        else:
            if not user_form.is_valid():
                for field, errors in user_form.errors.items():
                    for error in errors:
                        messages.error(request, f"Kullanıcı Bilgileri - {field}: {error}")
            if not author_form.is_valid():
                for field, errors in author_form.errors.items():
                    for error in errors:
                        messages.error(request, f"Editör Bilgileri - {field}: {error}")
    return render(request, 'account/authors-edit.html', {
        'user_form': user_form,
        'author_form': author_form,
        'author': author,
        'author_id': author.id
    })

@login_required
def editor_articles(request):
    # Superuser veya editör yetkisi olanlar erişebilir
    if not (request.user.is_superuser or (hasattr(request.user, 'author') and request.user.author.editor_article)):
        messages.error(request, "Bu sayfaya erişim yetkiniz bulunmamaktadır.")
        return redirect('index') # 'home' yerine 'index'e yönlendirme yapıyorum.
    
    articles = Article.objects.all().order_by('isHome', '-created_at')
    return render(request, 'account/editor-articles.html', {
        'articles': articles
    })
