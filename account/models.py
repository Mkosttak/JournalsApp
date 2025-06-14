from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_delete
from django.dispatch import receiver


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_image = models.ImageField(upload_to="author_profiles", default="author_profiles/default.png")
    bio = models.TextField(blank=True, null=True)
    resume = models.FileField(upload_to="author_resumes", blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    editor_article = models.BooleanField(default=False, help_text="Bu yazarın editör yetkisi")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

    @property
    def full_name(self):
        return f"{self.user.first_name} {self.user.last_name}"

    @property
    def articles_count(self):
        return self.user.article_set.filter(isHome=True).count()

@receiver(post_delete, sender=Author)
def delete_user_with_author(sender, instance, **kwargs):
    if instance.user:
        instance.user.delete()