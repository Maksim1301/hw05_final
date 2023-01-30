from django.urls import path

from . import views

app_name = 'posts'

urlpatterns = [
    # главная
    path('', views.index, name='index'),
    # посты группы
    path('group/<slug:slug>/',
         views.group_posts,
         name='group_list'),
    # страница входа
    path('create/',
         views.post_create,
         name='post_create'),
    # профайл пользователя
    path('profile/<str:username>/',
         views.profile,
         name='profile'),
    # посты по id
    path('posts/<int:post_id>/',
         views.post_detail,
         name='post_detail'),
    # редактирование поста по id
    path('posts/<int:post_id>/edit/',
         views.post_edit,
         name='post_edit'),
    # написание комментариев по id
    path('posts/<int:post_id>/comment/',
         views.add_comment,
         name='add_comment'),
    # страница подписок
    path('follow/',
         views.follow_index,
         name='follow_index'),
    # страница подписки на автора
    path('profile/<str:username>/follow/',
         views.profile_follow,
         name='profile_follow'),
    # страница отписки от автора
    path('profile/<str:username>/unfollow/',
         views.profile_unfollow,
         name='profile_unfollow'),
]
