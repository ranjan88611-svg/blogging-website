from django.contrib import admin
from .models import Category, Tag, Profile, Post, Comment, Like, Subscriber, PostView


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'created', 'featured')
    list_filter = ('status', 'created', 'featured', 'category')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('author',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'post', 'approved', 'created')
    list_filter = ('approved', 'created')
    search_fields = ('name', 'email', 'body')


admin.site.register(Profile)
admin.site.register(Like)
admin.site.register(Subscriber)
admin.site.register(PostView)
