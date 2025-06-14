from django import forms
from .models import Contact

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Adınız ve Soyadınız'}),
            'email': forms.EmailInput(attrs={'placeholder': 'E-posta Adresiniz'}),
            'subject': forms.TextInput(attrs={'placeholder': 'Mesajın Konusu'}),
            'message': forms.Textarea(attrs={'placeholder': 'Sorununuzu veya mesajınızı buraya yazın...', 'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
            self.fields[field].label = "" # Etiketleri kaldırıyoruz, placeholder yeterli