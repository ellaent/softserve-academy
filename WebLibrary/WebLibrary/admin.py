from django.contrib import admin

from .models import Book, Genre, Author, Comment, BookReview
from django.contrib.auth.admin import UserAdmin
from users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'is_active', 'date_joined', 'is_staff', 'role')
    filter_horizontal = ("groups", "user_permissions")


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    pass


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    pass


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug')
    def has_delete_permission(self, request, obj=None):
        print("Post: ", list(request.POST))
        # if request.POST and request.POST.get('action') == 'delete_selected':
        #     animals = Animal.objects.filter( id__in = request.POST.getlist('_selected_action') )
        #     print (animals)
        return True


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    pass


@admin.register(BookReview)
class BookReviewAdmin(admin.ModelAdmin):
    pass

