from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Article, Category, Author
from .forms import ArticleForm


class ArticleTests(TestCase):
    def setUp(self):
        """
        Her test öncesi çalışacak olan başlangıç ayarları.
        """
        self.client = Client()

        # Test için bir süper kullanıcı (admin) ve normal bir kullanıcı (yazar) oluştur
        self.admin_user = User.objects.create_superuser(username='admin_user', password='adminpassword123',
                                                        email='admin@test.com')
        self.author_user = User.objects.create_user(username='author_user', password='authorpassword123',
                                                    email='author@test.com')

        # Kullanıcılar için yazar profilleri oluştur
        self.admin_author = Author.objects.create(user=self.admin_user, full_name="Admin User", is_active=True,
                                                  is_admin=True)
        self.author_profile = Author.objects.create(user=self.author_user, full_name="Test Author")

        # Test kategorisi ve makalesi oluştur
        self.category = Category.objects.create(name='Teknoloji', slug='teknoloji')
        self.article = Article.objects.create(
            title='Test Başlık',
            slug='test-baslik',
            content='Bu bir test makalesidir.',
            author=self.author_profile,
            is_active=True,
            is_home=True
        )
        self.article.categories.add(self.category)

    ### MODEL TESTLERİ ###
    def test_category_model(self):
        """Kategori modelinin doğru oluşturulup oluşturulmadığını test eder."""
        self.assertEqual(str(self.category), 'Teknoloji')
        self.assertEqual(self.category.slug, 'teknoloji')

    def test_article_model(self):
        """Makale modelinin doğru oluşturulup oluşturulmadığını test eder."""
        self.assertEqual(str(self.article), 'Test Başlık')
        self.assertEqual(self.article.author.full_name, 'Test Author')
        self.assertTrue(self.article.is_active)
        self.assertIn(self.category, self.article.categories.all())

    ### URL ve VIEW TESTLERİ ###
    def test_home_page_view(self):
        """Ana sayfanın (index) düzgün çalışıp çalışmadığını test eder."""
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'articles/index.html')
        self.assertContains(response, self.article.title)

    def test_article_list_view(self):
        """Makale listeleme sayfasının düzgün çalışıp çalışmadığını test eder."""
        response = self.client.get(reverse('articles:articles'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'articles/list.html')
        self.assertContains(response, self.article.title)

    def test_article_detail_view(self):
        """Makale detay sayfasının düzgün çalışıp çalışmadığını test eder."""
        response = self.client.get(reverse('articles:detail', kwargs={'slug': self.article.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'articles/details.html')
        self.assertContains(response, self.article.title)
        self.assertContains(response, self.article.content)

    def test_articles_by_category_view(self):
        """Kategoriye göre makale listeleme sayfasının düzgün çalışıp çalışmadığını test eder."""
        response = self.client.get(reverse('articles:articles_by_category', kwargs={'slug': self.category.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'articles/list.html')
        self.assertContains(response, self.article.title)

    ### FORM VE YETKİLENDİRME TESTLERİ ###
    def test_article_create_view_unauthenticated(self):
        """Giriş yapmamış kullanıcının makale oluşturma sayfasına erişemediğini test eder."""
        response = self.client.get(reverse('articles:article-create'))
        self.assertEqual(response.status_code, 302)  # Login sayfasına yönlendirmeli
        self.assertRedirects(response, f"/account/login/?next={reverse('articles:article-create')}")

    def test_article_create_view_authenticated_author(self):
        """Giriş yapmış bir yazarın makale oluşturma sayfasını görebildiğini test eder."""
        self.client.login(username='author_user', password='authorpassword123')
        response = self.client.get(reverse('articles:article-create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'articles/article-create.html')
        self.assertIsInstance(response.context['form'], ArticleForm)

    def test_article_create_post_request(self):
        """Giriş yapmış bir yazarın yeni bir makale oluşturabildiğini test eder."""
        self.client.login(username='author_user', password='authorpassword123')
        new_article_data = {
            'title': 'Yeni Test Makalesi',
            'content': 'İçerik...',
            'categories': [self.category.id],
            'is_active': True,
        }
        response = self.client.post(reverse('articles:article-create'), data=new_article_data)

        # Başarılı bir post sonrası yönlendirme kontrolü
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('account:my-articles'))

        # Yeni makalenin veritabanında olup olmadığını kontrol et
        self.assertTrue(Article.objects.filter(title='Yeni Test Makalesi').exists())
        new_article = Article.objects.get(title='Yeni Test Makalesi')
        self.assertEqual(new_article.author, self.author_profile)

    def test_article_edit_view(self):
        """Bir yazarın kendi makalesini düzenleme sayfasına erişebildiğini test eder."""
        self.client.login(username='author_user', password='authorpassword123')
        response = self.client.get(reverse('articles:article-edit', kwargs={'slug': self.article.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'articles/article-edit.html')
        self.assertContains(response, self.article.title)

    def test_article_delete_view(self):
        """Bir yazarın kendi makalesini silebildiğini test eder."""
        self.client.login(username='author_user', password='authorpassword123')
        response = self.client.post(reverse('articles:article-delete', kwargs={'slug': self.article.slug}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('account:my-articles'))
        self.assertFalse(Article.objects.filter(slug=self.article.slug).exists())