from django.db import models

class Contact(models.Model):
    name = models.CharField(max_length=255, verbose_name="Ad Soyad")
    email = models.EmailField(verbose_name="E-posta")
    subject = models.CharField(max_length=255, verbose_name="Konu")
    message = models.TextField(verbose_name="Mesaj")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Gönderilme Tarihi")
    is_answered = models.BooleanField(default=False, verbose_name="Cevaplandı mı?")

    def __str__(self):
        return f"{self.name} - {self.subject}"

    class Meta:
        verbose_name = "İletişim Mesajı"
        verbose_name_plural = "İletişim Mesajları"
        ordering = ['-created_at']

class Subscriber(models.Model):
    email = models.EmailField(unique=True, max_length=254)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "Abone"
        verbose_name_plural = "Aboneler"