from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from datetime import datetime, timedelta, timezone, tzinfo
from django import forms

from . import settings


class Genre(models.Model):
    genre_id = models.AutoField(primary_key=True)
    name = models.CharField(_('Name'), max_length=200)

    def __str__(self):
        return self.name


class Author(models.Model):
    author_id = models.AutoField(primary_key=True)
    first_name = models.CharField(_('Name'), max_length=200)
    last_name = models.CharField(_('Surname'), max_length=200)
    slug = models.SlugField(_('Slug'), unique=True)

    def __str__(self):
        return str('%s %s' % (self.first_name, self.last_name))


class Book(models.Model):
    book_id = models.AutoField(primary_key=True)
    title = models.CharField(_('Name'), max_length=200)
    slug = models.SlugField(_('Slug'), unique=True)
    genres = models.ManyToManyField(Genre, related_name="genre", symmetrical=False)
    authors = models.ManyToManyField(Author, related_name="author", symmetrical=False)
    cover = models.ImageField(upload_to='', blank=True, null=True)
    description = models.TextField(_('Description'))
    viewCount = models.IntegerField(default=0)

    def incrementViewCount(self):
        self.viewCount += 1
        self.save()

    def get_absolute_url(self):
        return reverse("book_detail", kwargs={'book_slug': self.slug})

    def __str__(self):
        return self.title


class Comment(models.Model):
    book = models.ForeignKey(Book, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, related_name='comments',
                             on_delete=models.SET_NULL)
    text = models.TextField(_('Comment'))
    created_date = models.DateTimeField(default=datetime.now())
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)

    class Meta:
        ordering = ('-created_date', )

    def __str__(self):
        return 'comment from {}'.format(self.user)


class Like(models.Model):
    book = models.ForeignKey(Book, related_name='likes', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='likes', on_delete=models.CASCADE)

    class Meta:
        unique_together = (('book', 'user'),)

    def __str__(self):
        return '{} from {}'.format(self.book, self.user)


class BookReview(models.Model):
    review_id = models.AutoField(primary_key=True)
    book = models.ForeignKey(Book, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, related_name='reviews',
                             on_delete=models.SET_NULL)
    text = models.TextField(_('Review'))
    created_date = models.DateTimeField(default=datetime.now())
    is_approved = models.BooleanField(default=False)

    class Meta:
        ordering = ('-created_date', )

    def __str__(self):
        return 'review from {}'.format(self.user)


class ModeratorChoiceModel(models.Model):
    edit = forms.ChoiceField(widget=forms.RadioSelect)


# class BookReview(models.Model):
#     book = models.OneToOneField(
#         Book,
#         on_delete=models.CASCADE,
#         primary_key=True,
#     )
#     text = models.TextField(_('Description'))