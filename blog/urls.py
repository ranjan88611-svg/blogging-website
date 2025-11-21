from django.urls import path
from .views import (
    PostListView, PostDetailView, PostCreateView, PostUpdateView, PostDeleteView,
    like_post, publish_post, unpublish_post, dashboard, register, edit_profile, subscribe, subscribe_thanks, contact, about
)

urlpatterns = [
    path('', PostListView.as_view(), name='post_list'),
    path('post/new/', PostCreateView.as_view(), name='post_create'),
    path('post/<slug:slug>/edit/', PostUpdateView.as_view(), name='post_update'),
    path('post/<slug:slug>/delete/', PostDeleteView.as_view(), name='post_delete'),
    path('post/<slug:slug>/', PostDetailView.as_view(), name='post_detail'),
    path('post/<slug:slug>/like/', like_post, name='post_like'),
    path('post/<slug:slug>/publish/', publish_post, name='post_publish'),
    path('post/<slug:slug>/unpublish/', unpublish_post, name='post_unpublish'),
    path('dashboard/', dashboard, name='dashboard'),
    path('register/', register, name='register'),
    path('profile/edit/', edit_profile, name='profile_edit'),
    path('subscribe/', subscribe, name='subscribe'),
    path('subscribe/thanks/', subscribe_thanks, name='subscribe_thanks'),
    path('contact/', contact, name='contact'),
    path('about/', about, name='about'),
]
