from django.contrib import admin
from .models import User, Post, Message, Reply, Comment, Category

class PostAdmin(admin.ModelAdmin):
    list_display = ('creator', 'title')

# Register your models here.
admin.site.register(User)
admin.site.register(Post, PostAdmin)
admin.site.register(Message)
admin.site.register(Reply)
admin.site.register(Comment)
admin.site.register(Category)
