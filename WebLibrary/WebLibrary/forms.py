from django import forms
from django.contrib.auth import get_user_model
from .models import Comment, Book, Genre, Author, BookReview, Like
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field
from . import settings
import os
from django.core.files import File

User = get_user_model()

ip = forms.GenericIPAddressField(required=False)


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
        # fields = ('book', 'user', 'ip', 'text')


class LikeForm(forms.Form):

    class Meta:
        model = Like


class BookReviewApproveForm(forms.Form):

    class Meta:
        model = BookReview
        # fields = ('is_approved', )


class BookUpdateForm(forms.ModelForm):

    title = forms.TextInput()
    slug = forms.SlugField()
    genres = forms.ModelMultipleChoiceField(
        queryset=Genre.objects.all(),
        widget=forms.SelectMultiple
    )
    authors = forms.ModelMultipleChoiceField(
        queryset=Author.objects.all(),
        widget=forms.SelectMultiple
    )
    cover = forms.ImageField(allow_empty_file=True, required=False)
    description = forms.TextInput()

    def get_multiplechoice_set(self, obj, str):
        genres = Book._meta.get_field(str)
        return getattr(obj, genres.attname)

    class Meta:
        model = Book
        # title = 'title'
        fields = ('title', 'slug', 'authors', 'genres', 'cover', 'description')

    def __init__(self, *args, **kwargs):
        self.data = kwargs.get('initial')
        print("slug: ", self.data['slug'])
        obj = Book.objects.filter(slug=self.data['slug'])[0]
        title_object = Book._meta.get_field('title')
        description_object = Book._meta.get_field('description')
        cover_object = Book._meta.get_field('cover')
        self.data['title'] = getattr(obj, title_object.attname)
        self.data['description'] = getattr(obj, description_object.attname)
        self.data['cover'] = getattr(obj, cover_object.attname)
        print ("objects: ", self.data['title'], " | ", self.data['slug'], " | ", self.data['description'], "|",  self.data['cover'])
        self.title.initial = self.data['title']
        self.description.initial = self.data['description']

        path = os.path.join(settings.MEDIA_ROOT, str(self.data['cover']))
        # self.authors.initial = self.get_genres(obj)
        super(BookUpdateForm, self).__init__(*args, **kwargs)
        self.initial['genres'] = self.get_multiplechoice_set(obj, 'genres').all()
        self.initial['authors'] = self.get_multiplechoice_set(obj, 'authors').all()
        try:
            self.default_cover = open(path)
            self.fields['cover'].initial = File(self.default_cover)
        except:
            pass


class BookForm(forms.ModelForm):

    title = forms.TextInput()
    slug = forms.SlugField()
    genres = forms.ModelMultipleChoiceField(
        queryset=Genre.objects.all(),
        widget=forms.SelectMultiple
    )
    authors = forms.ModelMultipleChoiceField(
        queryset=Author.objects.all(),
        widget=forms.SelectMultiple
    )
    cover = forms.ImageField(allow_empty_file=True, required=False)
    description = forms.TextInput()

    class Meta:
        model = Book
        fields = ('title', 'slug', 'authors', 'genres', 'cover', 'description')


class AuthorForm(forms.ModelForm):

    class Meta:
        model = Author
        fields = ('first_name', 'last_name', 'slug', )


class GenreForm(forms.ModelForm):

    class Meta:
        model = Genre
        fields = ('name', )


class BookReviewForm(forms.ModelForm):
    text = forms.TextInput()

    class Meta:
        model = BookReview
        fields = ('text', )


class ModeratorChoiceForm(forms.Form):
    edit = forms.ChoiceField(required=True, widget=forms.RadioSelect(
        attrs={'onchange': 'submit();',}), choices=(('edit', 'edit on'), ('non-edit', 'edit off'), ), label="Edit mode")

    def if_checked(self):
        if self.edit == 'edit':
            return 'checked'
        else:
            return ''
        # for key in self.initial_fields:
        #     if hasattr(self.person, key):
        #         self.fields[k].initial = getattr(self.person, key)
        # super(RegisterForm, self).__init__(*args, **kwargs)

