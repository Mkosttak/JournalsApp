from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.forms import widgets, ModelForm, FileInput, TextInput, Textarea, EmailInput, PasswordInput
from django.contrib import messages
from .models import Author
from django import forms


class LoginUserForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget = widgets.TextInput(attrs={"class": "form-control"})
        self.fields["password"].widget = widgets.PasswordInput(attrs={"class": "form-control"})

    def clean_username(self):
        username = self.cleaned_data.get("username")

        if username == "admin":
            messages.add_message(self.request, messages.SUCCESS, "Admin Hoşgeldin!")
        return username


class NewUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].widget = widgets.PasswordInput(attrs={"class": "form-control"})
        self.fields["password2"].widget = widgets.PasswordInput(attrs={"class": "form-control"})
        self.fields["first_name"].widget = widgets.TextInput(attrs={"class": "form-control"})
        self.fields["last_name"].widget = widgets.TextInput(attrs={"class": "form-control"})
        self.fields["username"].widget = widgets.TextInput(attrs={"class": "form-control"})
        self.fields["email"].widget = widgets.EmailInput(attrs={"class": "form-control"})
        self.fields["email"].required = True
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            self.add_error("email", "Bu email adresi zaten kayıtlı.")

        return email


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
        fields = ('profile_image', 'bio', 'resume', 'is_approved')
        widgets = {
            'profile_image': FileInput(attrs={"class": "form-control"}),
            'bio': Textarea(attrs={"class": "form-control", "rows": 5}),
            'resume': FileInput(attrs={"class": "form-control"}),
            'is_approved': forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and not user.is_superuser:
            self.fields.pop('is_approved', None)

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