from django import forms
from .models import Article, Category
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

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if not file:
            raise forms.ValidationError("Lütfen bir PDF dosyası yükleyin.")
        return file

class ArticleEditForm(forms.ModelForm):
    categories = forms.ModelChoiceField(queryset=Category.objects.all(), empty_label="Kategori Seçiniz", required=True, error_messages={'required': "Sadece bir tane Kategori seçin."})

    class Meta:
        model = Article
        fields = [
            'title', 'description', 'file', 
            'keywords', 'admin_note', 'isHome'
        ]
        labels = {
            'title': 'Başlık',
            'description': 'Açıklama',
            'file': 'PDF Dosyası',
            'keywords': 'Anahtar Kelimeler',
            'admin_note': 'Editör Notu',
            'isHome': 'Ana Sayfada Göster',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
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

    def clean_categories(self):
        category = self.cleaned_data.get('categories')
        if not category:
            raise forms.ValidationError("Sadece bir tane Kategori seçin.")
        return category

class UserArticleEditForm(forms.ModelForm):
    categories = forms.ModelChoiceField(queryset=Category.objects.all(), empty_label="Kategori Seçiniz", required=True, error_messages={'required': "Sadece bir tane Kategori seçin."})

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
    
    def clean_categories(self):
        category = self.cleaned_data.get('categories')
        if not category:
            raise forms.ValidationError("Sadece bir tane Kategori seçin.")
        return category

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.file:
            self.fields['file'].file_display_name = os.path.basename(self.instance.file.name)

