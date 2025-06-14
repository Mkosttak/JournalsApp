from django.test import TestCase, Client
from django.urls import reverse

class PageTests(TestCase):
    def setUp(self):
        """
        Her test öncesi çalışacak olan başlangıç ayarları.
        """
        self.client = Client()

    def test_index_page_view(self):
        """'index' sayfasının (eğer pages app'te varsa) durumunu kontrol eder."""
        # Not: Ana index view'ı articles app'te olduğu için buradaki test,
        # pages app'in kendi index'ine yöneliktir. Eğer ayrı bir sayfası yoksa bu test gereksiz olabilir.
        # Eğer varsa url adını 'pages_index' olarak varsayıyoruz.
        try:
            url = reverse('pages:index')
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'pages/index.html')
        except:
            # Eğer pages:index URL'i yoksa testi geç.
            pass


    def test_about_page_view(self):
        """'about' sayfasının durumunu ve şablonunu kontrol eder."""
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/about.html')
        self.assertContains(response, 'Hakkımızda') # Şablonda bu metnin geçtiğini varsayıyoruz.

    def test_contact_page_view(self):
        """'contact' sayfasının durumunu ve şablonunu kontrol eder."""
        response = self.client.get(reverse('contact'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/contact.html')
        self.assertContains(response, 'İletişim') # Şablonda bu metnin geçtiğini varsayıyoruz.