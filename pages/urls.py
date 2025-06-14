from django.urls import path
from . import views

app_name = 'pages'

urlpatterns = [
    path("", views.index, name="index"),
    path("index/", views.index, name="index"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("contact/admin-contact", views.admin_contact, name="admin_contact"),
    path("contact/admin-contact<int:message_id>/", views.get_message, name="get_message"),
    path("contact/admin-contact<int:message_id>/reply/", views.reply_message, name="reply_message"),
    path("contact/admin-contact<int:message_id>/delete/", views.delete_message, name="delete_message"),
    path("contact/admin-contact<int:message_id>/toggle-status/", views.toggle_message_status, name="toggle_message_status"),
]