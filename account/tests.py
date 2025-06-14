from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Author


class AccountTests(TestCase):

    def setUp(self):
        """
        Her test öncesi çalışacak olan başlangıç ayarları.
        """
        self.client = Client()

        # Test için bir kullanıcı ve yazar profili oluştur
        self.user = User.objects.create_user(username='testuser', password='testpassword123', email='test@test.com')
        self.author = Author.objects.create(user=self.user, full_name="Test Kullanıcı")

    ### MODEL TESTLERİ ###
    def test_author_model(self):
        """Yazar modelinin doğru oluşturulup oluşturulmadığını test eder."""
        self.assertEqual(str(self.author), self.user.username)
        self.assertEqual(self.author.full_name, "Test Kullanıcı")
        self.assertTrue(self.author.is_active)
        self.assertFalse(self.author.is_admin)

    ### VIEW VE URL TESTLERİ ###
    def test_login_view(self):
        """Giriş sayfasının ve işleminin doğruluğunu test eder."""
        # GET request
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/login.html')

        # POST request (başarılı giriş)
        login_data = {'username': 'testuser', 'password': 'testpassword123'}
        response = self.client.post(reverse('login'), data=login_data)
        self.assertEqual(response.status_code, 302)  # Başarılı girişte yönlendirme
        self.assertRedirects(response, reverse('index'))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_logout_view(self):
        """Çıkış işleminin doğruluğunu test eder."""
        self.client.login(username='testuser', password='testpassword123')
        self.assertTrue(self.client.session['_auth_user_id'])

        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('index'))
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_register_view(self):
        """Kayıt sayfasının ve işleminin doğruluğunu test eder."""
        # GET request
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/register.html')

        # POST request (yeni kullanıcı kaydı)
        register_data = {
            'full_name': 'Yeni Kullanıcı',
            'username': 'newuser',
            'email': 'new@test.com',
            'password': 'newpassword123',
            're_password': 'newpassword123'
        }
        response = self.client.post(reverse('register'), data=register_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/login.html')  # Başarılı kayıt sonrası login'e yönlendirir
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertTrue(Author.objects.filter(full_name='Yeni Kullanıcı').exists())

    def test_profile_view_authenticated(self):
        """Giriş yapmış kullanıcının profil sayfasına erişimini test eder."""
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.get(reverse('account:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/profile.html')
        self.assertEqual(response.context['author'], self.author)

    def test_profile_edit_view(self):
        """Profil düzenleme sayfasının ve işleminin doğruluğunu test eder."""
        self.client.login(username='testuser', password='testpassword123')

        # GET request
        response = self.client.get(reverse('account:profile-edit'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/profile_edit.html')

        # POST request (profil güncelleme)
        updated_data = {
            'full_name': 'Güncel İsim',
            'email': 'updated@test.com'
        }
        response = self.client.post(reverse('account:profile-edit'), data=updated_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('account:profile'))

        # Verilerin güncellendiğini kontrol et
        self.user.refresh_from_db()
        self.author.refresh_from_db()
        self.assertEqual(self.author.full_name, 'Güncel İsim')
        self.assertEqual(self.user.email, 'updated@test.com')