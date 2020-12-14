from django.contrib import admin
from .models import User, Post, Message, Reply, Comment, Category, NoRegistrationCode, ImportantAdminMessages
from admin_auto_filters.filters import AutocompleteFilter



class PostFilter(AutocompleteFilter):
    title = 'صاحب المنشور' # display title
    field_name = 'creator' # name of the foreign key field

class UserFilter(AutocompleteFilter):
    title = 'الصاحب' # display title
    field_name = 'user' # name of the foreign key field

class MessageFilter(AutocompleteFilter):
    title = 'المستقبل' # display title
    field_name = 'receiver' # name of the foreign key field

class PostAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ['title']
    list_filter = ("category", "created", "isActive", PostFilter)

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'continent')
    search_fields = ['username','email' , 'continent']
    list_filter = ("email_active", "stay_logged_in", "isBlocked")

class NoRegistrationCodeAdmin(admin.ModelAdmin):
    list_display = ('email', 'continent')
    search_fields = ['email' , 'continent']
    list_filter = ('continent',)

class MessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'receiver', 'title')
    search_fields = ['title', 'content']
    list_filter = ("is_read", "created", UserFilter, MessageFilter)

class ReplyAdmin(admin.ModelAdmin):
    list_display = ('user', 'content')
    search_fields = ['content']
    list_filter = ("isActive", "created", UserFilter)

class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'content')
    search_fields = ['content']
    list_filter = ("isActive", "created", UserFilter)

class AdminMessages(admin.ModelAdmin):
    list_display = ('message', 'show')



# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(Reply, ReplyAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Category)
admin.site.register(NoRegistrationCode, NoRegistrationCodeAdmin)
admin.site.register(ImportantAdminMessages, AdminMessages)
