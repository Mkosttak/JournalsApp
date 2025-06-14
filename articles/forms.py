from django import forms
from .models import Article
import os


class ArticleCreateForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'description', 'file', 'keywords']
        labels = {
            'title': 'Başlık',
            'description': 'Açıklama',
            'file': 'PDF Dosyası',
            'keywords': 'Anahtar Kelimeler',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'keywords': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Anahtar kelimeleri virgülle ayırarak girin'
            }),
        }

class ArticleEditForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = [
            'title', 'description', 'file', 'categories',
            'keywords', 'admin_note', 'isHome'
        ]
        labels = {
            'title': 'Başlık',
            'description': 'Açıklama',
            'file': 'PDF Dosyası',
            'categories': 'Kategoriler',
            'keywords': 'Anahtar Kelimeler',
            'admin_note': 'Editör Notu',
            'isHome': 'Ana Sayfada Göster',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'categories': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'keywords': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Anahtar kelimeleri virgülle ayırarak girin'
            }),
            'admin_note': forms.Textarea(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.file:
            self.fields['file'].file_display_name = os.path.basename(self.instance.file.name)

class UserArticleEditForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'description', 'file', 'keywords']
        labels = {
            'title': 'Başlık',
            'description': 'Açıklama',
            'file': 'PDF Dosyası',
            'keywords': 'Anahtar Kelimeler',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'keywords': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Anahtar kelimeleri virgülle ayırarak girin'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.file:
            self.fields['file'].file_display_name = os.path.basename(self.instance.file.name)

