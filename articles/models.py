from django.utils.text import slugify
from django.db import models
from django.contrib.auth.models import User
import os
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError


def validate_pdf(value):
    ext = os.path.splitext(value.name)[1]
    if ext.lower() != '.pdf':
        raise ValidationError('Sadece PDF dosyaları yüklenebilir.')

def article_file_upload_to(instance, filename):
    ext = os.path.splitext(filename)[1]
    return f'articles/{instance.slug}{ext}'

class Article(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='articles', blank=True, null=True)
    file = models.FileField(
        upload_to=article_file_upload_to,
        blank=True,
        null=True,
        validators=[validate_pdf]
    )
    date = models.DateField(auto_now=True)
    isHome = models.BooleanField(default=False)
    slug = models.SlugField(null=False, blank=True, unique=True)
    categories = models.ForeignKey("Category",on_delete=models.SET_NULL, null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    admin_note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_admin_note_read_by_author = models.BooleanField(default=True)
    keywords = models.TextField(
        help_text="Anahtar kelimeleri virgülle ayırarak girin",
        blank=True,
        null=True
    )

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.keywords:
            # Anahtar kelimeleri virgülle ayır, her bir kelimenin başındaki/sonundaki boşlukları temizle
            # ve boş olanları filtrele
            cleaned_keywords = [k.strip() for k in self.keywords.split(',') if k.strip()]
            # Temizlenmiş anahtar kelimeleri tek virgülle birleştir
            self.keywords = ','.join(cleaned_keywords)

        if not self.slug:
            base_slug = slugify(self.title)
            unique_slug = base_slug
            num = 1
            while Article.objects.filter(slug=unique_slug).exclude(pk=self.pk).exists():
                unique_slug = f"{base_slug}-{num}"
                num += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-updated_at']

class Category(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(null=False, default="", unique=True, db_index=True)
    order = models.PositiveIntegerField(default=0, blank=False, null=False, unique=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.pk:  # Yeni bir kategori ise
            last_category = Category.objects.all().order_by('-order').first()
            if last_category:
                self.order = last_category.order + 1
            else:
                self.order = 1
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-order']
        pass
