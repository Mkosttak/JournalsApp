from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_delete, pre_save
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

@receiver(pre_save, sender=Author)
def auto_delete_old_files_on_update(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_instance = Author.objects.get(pk=instance.pk)
        old_profile_image = old_instance.profile_image
        old_resume = old_instance.resume
    except Author.DoesNotExist:
        return False

    new_profile_image = instance.profile_image
    new_resume = instance.resume

    # Delete old profile image if it's changed and not the default image
    if old_profile_image and old_profile_image != new_profile_image and 'default.png' not in old_profile_image.name:
        old_profile_image.delete(save=False)

    # Delete old resume if it's changed
    if old_resume and old_resume != new_resume:
        old_resume.delete(save=False)

@receiver(post_delete, sender=Author)
def auto_delete_files_on_delete(sender, instance, **kwargs):
    if instance.profile_image and 'default.png' not in instance.profile_image.name:
        instance.profile_image.delete(save=False)
    if instance.resume:
        instance.resume.delete(save=False)