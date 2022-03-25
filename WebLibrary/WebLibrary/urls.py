"""WebLibrary URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from . import views
from .views import BookListView, BookOverview

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', BookListView.as_view(), name="home"),
    path('<slug:book_slug>/$', BookOverview.as_view(), name='book_detail'),
    path('<slug:book_slug>/reviews/', views.BookReviewListView.as_view(), name='book_reviews'),
    path('<slug:book_slug>/reviews/all/', views.AllReviewList.as_view(), name='all_book_reviews'),
    path('<slug:book_slug>/reviews/<int:review_id>/', views.BookReviewOverview.as_view(), name='book_review'),
    path('<slug:book_slug>/reviews/all/<int:review_id>/', views.BookReviewOverviewAll.as_view(), name='book_review_all'),
    path('<slug:book_slug>/reviews/all/<int:review_id>/update', views.BookReviewApprove.as_view(), name='book_review_update'),
    path('<slug:book_slug>/review/create/', views.BookOverviewCreateView.as_view(), name='book_review_create'),
    path('<slug:book_slug>/comment/', views.CommentProductView.as_view(), name='comment_product'),
    path('<slug:book_slug>/update/', views.BookUpdateView.as_view(), name='book_update'),
    path('<slug:book_slug>/delete/', views.BookDeleteView.as_view(), name='book_delete'),
    path('<slug:book_slug>/like/', views.LikeToggleView.as_view(), name='like_toggle'),
    path('book/add/', views.BookCreateView.as_view(), name='book_add'),
    path('author/add/', views.AuthorCreateView.as_view(), name='author_add'),
    path('genre/add/', views.GenreCreateView.as_view(), name='genre_add'),
    path('<str:sort>', views.PopularBookListView.as_view(), name='sort_books'),
    path('users/', include("users.urls")),
    path('users/', include('django.contrib.auth.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
              + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
