from django.urls import path
from . import views

app_name = 'account'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/change-password/', views.change_password, name='change_password'),
    path('my-articles/', views.my_articles, name='my_articles'),
    path('editor-articles/', views.editor_articles, name='editor_articles'),
    path('authors/', views.authors_list, name='authors_list'),
    path('admin-authors/', views.admin_authors, name='admin_authors'),
    path('admin-editors/<int:author_id>/edit/', views.authors_edit, name='authors_edit'),
    path('admin/editors/delete/<int:id>/', views.author_delete, name='author_delete'),
    path('author/<int:author_id>/', views.author_detail, name='author_detail'),
]