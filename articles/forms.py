from django import forms
from .models import Article, Category
import os


class ArticleCreateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Sadece editör ve superuser için kategori alanını dinamik olarak ekle
        if user and (user.is_staff or user.is_superuser):
            self.fields['categories'] = forms.ModelChoiceField(
                queryset=Category.objects.all(), 
                empty_label="Kategori Seçiniz", 
                required=True, 
                error_messages={'required': "Lütfen bir kategori seçin."}
            )
        self.fields['file'].required = True # PDF alanı zorunlu yapıldı

    class Meta:
        model = Article
        fields = ['title', 'description', 'file', 'keywords'] # categories buradan kaldırıldı
        labels = {
            'title': 'Başlık',
            'description': 'Açıklama',
            'file': 'PDF Dosyası',
            'keywords': 'Anahtar Kelimeler',
            # 'categories': 'Kategori', # categories label'ı da buradan kaldırıldı
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
            'keywords', 'admin_note', 'isHome', 'categories'
        ]
        labels = {
            'title': 'Başlık',
            'description': 'Açıklama',
            'file': 'PDF Dosyası',
            'keywords': 'Anahtar Kelimeler',
            'admin_note': 'Editör Notu',
            'isHome': 'Ana Sayfada Göster',
            'categories': 'Kategori',
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
    categories = forms.ModelChoiceField(queryset=Category.objects.all(), empty_label="Kategori Seçiniz", required=False)

    class Meta:
        model = Article
        fields = ['title', 'description', 'file', 'keywords', 'categories']
        labels = {
            'title': 'Başlık',
            'description': 'Açıklama',
            'file': 'PDF Dosyası',
            'keywords': 'Anahtar Kelimeler',
            'categories': 'Kategori',
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
        # Bu form normal kullanıcılar için de kullanılabileceğinden, eğer kategori alanı gizliyse
        # ve boş geliyorsa validasyon hatası vermemelidir.
        # Eğer alan required=False ise bu metot gerekli değildir, Django otomatik halleder.
        # ForeignKey alanları için Django, null=True ise otomatik olarak boş değeri kabul eder.
        return self.cleaned_data.get('categories')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.file:
            self.fields['file'].file_display_name = os.path.basename(self.instance.file.name)

