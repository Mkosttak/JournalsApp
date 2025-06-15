from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.forms import widgets, ModelForm, FileInput, TextInput, Textarea, EmailInput, PasswordInput
from django.contrib import messages
from .models import Author
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password


class LoginUserForm(forms.Form):
    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email adresiniz"})
    )
    password = forms.CharField(
        label='Şifre',
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Şifreniz"})
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if email and password:
            try:
                user = User.objects.get(email=email)
                if not user.check_password(password):
                    raise forms.ValidationError("Email veya şifre hatalı!")
                cleaned_data['user'] = user
            except User.DoesNotExist:
                raise forms.ValidationError("Bu email adresi ile kayıtlı bir kullanıcı bulunamadı.")
        return cleaned_data


class RegisterUserForm(UserCreationForm):
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email adresiniz"})
    )
    first_name = forms.CharField(
        label='Ad',
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Adınız"})
    )
    last_name = forms.CharField(
        label='Soyad',
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Soyadınız"})
    )
    password1 = forms.CharField(
        label='Şifre',
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Şifreniz"}),
        help_text='''<ul>
            <li>En az 8 karakter uzunluğunda olmalı.</li>
        </ul>'''
    )
    password2 = forms.CharField(
        label='Şifre Tekrar',
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Şifrenizi tekrar girin"}),
        help_text='Lütfen şifrenizi tekrar girin.'
    )

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Bu email adresi zaten kullanılıyor!")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['email']  # Email'i username olarak kullan
        if commit:
            user.save()
        return user


class UserPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["old_password"].widget = widgets.PasswordInput(attrs={"class": "form-control"})
        self.fields["new_password1"].widget = widgets.PasswordInput(attrs={"class": "form-control"})
        self.fields["new_password2"].widget = widgets.PasswordInput(attrs={"class": "form-control"})


class AuthorProfileForm(ModelForm):
    clear_resume = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput())
    clear_profile_image = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput())

    class Meta:
        model = Author
        fields = ('profile_image', 'bio', 'resume', 'is_approved', 'editor_article')
        widgets = {
            'profile_image': FileInput(attrs={"class": "form-control"}),
            'bio': Textarea(attrs={"class": "form-control", "rows": 5}),
            'resume': FileInput(attrs={"class": "form-control"}),
            'is_approved': forms.CheckboxInput(attrs={"class": "form-check-input"}),
            'editor_article': forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Kullanıcı admin değilse bu alanları formdan çıkar
        if user and not user.is_superuser:
            self.fields.pop('is_approved', None)
            self.fields.pop('editor_article', None)
        # Add a custom attribute to store the original resume file name for JavaScript
        if self.instance and self.instance.resume and self.instance.resume.name:
            self.fields['resume'].widget.attrs['data-original-name'] = self.get_resume_file_display_name()

    def get_resume_file_display_name(self):
        if self.instance.resume and self.instance.resume.name:
            return self.instance.resume.name.split('/')[-1]
        return ""

    def clean_resume(self):
        resume = self.cleaned_data.get('resume')
        clear_resume = self.cleaned_data.get('clear_resume')

        if clear_resume:
            return None  # Set resume to None if clear_resume is True

        if resume:
            if resume.size > 5 * 1024 * 1024:  # 5MB
                raise forms.ValidationError('Dosya boyutu 5MB\'dan büyük olamaz.')
            if not resume.name.lower().endswith('.pdf'):
                raise forms.ValidationError('Sadece PDF formatında dosya yükleyebilirsiniz.')
        # If no new resume is uploaded, and clear_resume is false, retain the existing one
        elif self.instance and self.instance.resume and not clear_resume:
            return self.instance.resume
        return resume

    def clean_profile_image(self):
        image = self.cleaned_data.get('profile_image')
        
        # If no new image is uploaded, retain the existing one or use default
        if not image:
            if self.instance and self.instance.profile_image:
                return self.instance.profile_image
            # If no instance or no existing image, let the model default handle it (if default is set)
            return None # Or forms.ImageField().clean(None) for consistent handling of empty
            
        # Existing validation for uploaded images
        if image.size > 2 * 1024 * 1024:  # 2MB
            raise forms.ValidationError('Profil fotoğrafı 2MB\'dan büyük olamaz.')
        if not image.name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
            raise forms.ValidationError('Sadece JPG, JPEG, PNG veya GIF formatında dosya yükleyebilirsiniz.')
        return image


class UserProfileForm(ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')
        widgets = {
            'first_name': TextInput(attrs={"class": "form-control"}),
            'last_name': TextInput(attrs={"class": "form-control"}),
            'email': EmailInput(attrs={"class": "form-control", "readonly": "readonly"}),
        }


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(widget=EmailInput(attrs={"class": "form-control", "readonly": "readonly"}))
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']