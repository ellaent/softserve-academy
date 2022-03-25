from django.shortcuts import render
from .models import Book, Comment, BookReview, Like
from users.models import User
from .forms import CommentForm, BookUpdateForm, ModeratorChoiceForm, BookReviewForm, LikeForm, BookForm, AuthorForm, GenreForm, BookReviewApproveForm
from django.http import HttpResponse
from django.views.generic import ListView, DetailView, FormView, TemplateView
from django.db.models import Subquery, OuterRef
from operator import itemgetter
from django.db.models import Q
import datetime
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
# from braces.views import JSONResponseMixin, AjaxResponseMixin
from django.http import Http404
from django.db.models.signals import post_save
from django.core.paginator import Paginator


def get_ip_from_request(request):
  x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
  if x_forwarded_for:
    ip = x_forwarded_for.split(',')[0]
  else:
    ip = request.META.get('REMOTE_ADDR')
  return ip


def get_edit_mode(obj):
  return obj.request.GET.get('edit')


class BookListView(ListView):
  model = Book
  paginate_by = 8
  ordering = ['book_id']
  template_name = 'index.html'
  slug_url_kwarg = 'book_slug'

  def get_queryset(self):
    search_book = self.request.GET.get('search')
    if search_book:
      self.queryset = Book.objects.filter(Q(title__icontains=search_book) & Q(description__icontains=search_book))
    else:
      self.queryset = Book.objects.all().order_by("book_id")
    return self.queryset

  def get_context_data(self, **kwargs):
    if self.request.method == 'GET' and 'edit' in self.request.GET:
      self.request.session['edit_mode'] = get_edit_mode(self)
    try:
      print("list mode: ", self.request.session['edit_mode'])
    except:
      pass

    context = super(BookListView, self).get_context_data()
    context['book'] = Book.objects.get_queryset()
    search_book = self.request.GET.get('search')
    if search_book:
      context['search'] = context['book_list'].count()
      context['search_name'] = search_book
    return context


class PopularBookListView(ListView):
  model = Book
  # paginate_by = 8
  ordering = ['viewCount']
  template_name = 'popular_books.html'

  def get_context_data(self, **kwargs):
    context = super(PopularBookListView, self).get_context_data(**kwargs)
    if self.kwargs['sort'] == 'popular':
      books = Book.objects.all().order_by('-viewCount')[:8]
    else:
      books = Book.objects.all().order_by('title')[:8]
    context["books"] = books
    return context


class BookOverview(DetailView):
  model = Book
  slug_url_kwarg = 'book_slug'
  template_name = 'book_overview.html'
  book = None

  def get_context_data(self, **kwargs):

    if self.request.method == 'GET' and 'edit' in self.request.GET:
      self.request.session['edit_mode'] = get_edit_mode(self)
    book = Book.objects.filter(slug=self.kwargs['book_slug'])[0]
    book.incrementViewCount()
    print("Count: ", book.viewCount)

    context = {'book': book}
    """
    Need to make it with annotate !!!
    """
    genres = list(book.genres.all())  # finds all genres of book from overview
    books = list(Book.objects.all())  # to see all books
    result = list()
    for i in books:
      if i == book:
        continue
      book_genres = list(i.genres.all())
      result.append([len(list(set(genres) & set(book_genres))), i])  # append common genres and count
    related_books = (sorted(result, key=itemgetter(0), reverse=True))[:4]
    related_books = [x[1] for x in related_books]
    context['related_books'] = related_books

    _list = book.comments.filter(parent=None).select_related('user')
    paginator = Paginator(_list, 2)
    page = self.request.GET.get('page')
    context['comments'] = paginator.get_page(page)

    reviews_count = book.reviews.filter(is_approved=True).count()
    context['reviews_count'] = reviews_count

    if self.request.user.is_anonymous:
      pass
    else:
      if Like.objects.filter(user=self.request.user, book=book):
        context['liked'] = True
      else:
        context['liked'] = False
    return context


class BookReviewListView(ListView):
  model = BookReview
  template_name = 'book_reviews.html'
  slug_url_kwarg = 'book_slug'

  def get_context_data(self, **kwargs):
    if self.request.method == 'GET' and 'edit' in self.request.GET:
      self.request.session['edit_mode'] = get_edit_mode(self)
    book = Book.objects.filter(slug=self.kwargs['book_slug'])[0]
    context = {'book': book}
    _list = book.reviews.filter(is_approved=True).select_related('user')
    paginator = Paginator(_list, 3)
    page = self.request.GET.get('page')
    context['reviews'] = paginator.get_page(page)
    return context


class BookReviewOverview(DetailView):
  model = Book
  template_name = 'book_review_overview.html'
  slug_url_kwarg = 'book_slug'

  def get_context_data(self, **kwargs):
    if self.request.method == 'GET' and 'edit' in self.request.GET:
      self.request.session['edit_mode'] = get_edit_mode(self)
    context = super(BookReviewOverview, self).get_context_data(**kwargs)
    book = Book.objects.filter(slug=self.kwargs['book_slug'])[0]
    review = BookReview.objects.filter(review_id=self.kwargs['review_id'])[0]
    context['book'] = book
    context['review'] = review
    return context


class CommentProductView(FormView):
    http_method_names = ('post',)
    form_class = CommentForm
    template_name = 'book_overview.html'
    book = None
    text = None

    def form_valid(self, form, **kwargs):
      print("REQQ: ", self.request.POST)
      book_slug = self.request.POST.get('book_slug')
      user_id = self.request.POST.get('user_id')
      user = User.objects.filter(id=user_id)[0]
      book = Book.objects.filter(slug=book_slug)[0]
      text = form.cleaned_data['text']

      parent_obj = None
      try:
        parent_id = int(self.request.POST.get('parent_id'))
      except:
        parent_id = None
      if parent_id:
        parent_obj = Comment.objects.get(id=parent_id)
        if parent_obj:
          reply_comment = Comment.objects.create(user=user, book=book, text=text, parent=parent_obj)
          reply_comment.save()
      else:
        comment = Comment.objects.create(user=user, book=book, text=text)
        comment.save()
      return HttpResponseRedirect(reverse_lazy('book_detail', kwargs={'book_slug': book_slug}))


class LikeToggleView(FormView):
  http_method_names = ('post',)
  form_class = LikeForm
  template_name = 'book_overview.html'
  book = None

  def form_valid(self, form):
    self.user = self.request.user
    user_id = self.request.POST.get('user')
    book_id = self.request.POST.get('book')
    user = User.objects.filter(id=user_id)[0]
    book = Book.objects.filter(book_id=book_id)[0]
    like, created = Like.objects.get_or_create(user=user, book=book)
    if created:
      print("yes")
      like.save()
    else:
      like.delete()
    return redirect(self.request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))


class BookOverviewCreateView(CreateView):
  # http_method_names = ('post',)
  form_class = BookReviewForm
  template_name = 'book_review_create.html'
  slug_url_kwarg = 'book_slug'

  def get_context_data(self, **kwargs):
    context = super(BookOverviewCreateView, self).get_context_data(**kwargs)
    context['book'] = Book.objects.filter(slug=self.request.resolver_match.kwargs["book_slug"])[0]
    return context

  def form_valid(self, form, **kwargs):
    print("REQQ: ", self.request.POST)
    book_slug = self.request.POST.get('book_slug')
    user_id = self.request.POST.get('user_id')
    user = User.objects.filter(id=user_id)[0]
    book = Book.objects.filter(slug=book_slug)[0]
    text = form.cleaned_data['text']
    review = BookReview.objects.create(user=user, book=book, text=text)
    review.save()
    return HttpResponseRedirect(reverse_lazy('book_reviews', kwargs={'book_slug': book_slug}))


class BookCreateView(CreateView):
  form_class = BookForm
  template_name = 'model_add.html'
  # success_url = 'success'

  def get_context_data(self, **kwargs):
    context = super(BookCreateView, self).get_context_data(**kwargs)
    context['book'] = True
    context['model'] = 'book'
    return context

  def form_valid(self, form, **kwargs):
    book_slug = form.cleaned_data['slug']
    form.save()
    return HttpResponseRedirect(reverse_lazy('book_detail', kwargs={'book_slug': book_slug}))


class AuthorCreateView(CreateView):
  form_class = AuthorForm
  template_name = 'model_add.html'
  success_url = '/'

  def get_context_data(self, **kwargs):
    context = super(AuthorCreateView, self).get_context_data(**kwargs)
    context['model'] = 'author'
    return context


class GenreCreateView(CreateView):
  form_class = GenreForm
  template_name = 'model_add.html'
  success_url = '/'

  def get_context_data(self, **kwargs):
    context = super(GenreCreateView, self).get_context_data(**kwargs)
    context['model'] = 'genre'
    return context


class BookUpdateView(UpdateView):
  model = Book
  form_class = BookUpdateForm
  slug_url_kwarg = 'book_slug'
  template_name = 'book_update.html'

  def get_form_kwargs(self):
    kwargs = super(BookUpdateView, self).get_form_kwargs()
    kwargs['initial']['slug'] = self.kwargs['book_slug']
    print("kwargs: ", kwargs['initial']['slug'])
    return kwargs

  def get_success_url(self):
    slug = self.kwargs["book_slug"]
    return reverse_lazy("book_detail", kwargs={"book_slug": slug})


class BookDeleteView(DeleteView):
  model = Book
  slug_url_kwarg = 'book_slug'
  success_url = "/"

  def get_context_data(self, **kwargs):
    context = super(BookDeleteView, self).get_context_data(**kwargs)
    context['book'] = kwargs['object']
    print(kwargs)
    return context


class AllReviewList(ListView):
  model = BookReview
  template_name = 'book_reviews_all.html'
  slug_url_kwarg = 'book_slug'

  def get_context_data(self, **kwargs):
    print(self.request.GET)
    book = Book.objects.filter(slug=self.kwargs['book_slug'])[0]
    context = {'book': book}
    _list = book.reviews.all().select_related('user')
    paginator = Paginator(_list, 3)
    page = self.request.GET.get('page')
    context['reviews'] = paginator.get_page(page)
    return context


class BookReviewOverviewAll(DetailView):
  model = Book
  template_name = 'book_review_overview_all.html'
  slug_url_kwarg = 'book_slug'

  def get_context_data(self, **kwargs):
    context = super(BookReviewOverviewAll, self).get_context_data(**kwargs)
    book = Book.objects.filter(slug=self.kwargs['book_slug'])[0]
    review = BookReview.objects.filter(review_id=self.kwargs['review_id'])[0]
    context['book'] = book
    context['review'] = review
    context['all'] = True
    return context


class BookReviewApprove(FormView):
    http_method_names = ('post',)
    model = BookReview
    form_class = BookReviewApproveForm
    template_name = 'book_review_overview_all.html'
    # book = None

    def form_valid(self, form):
      book_slug = self.request.POST.get('book_slug')
      review_id = self.request.POST.get('review_id')
      book = Book.objects.filter(slug=book_slug)[0]
      review = BookReview.objects.filter(review_id=review_id)[0]
      if review.is_approved:
        review.is_approved = False
      else:
        review.is_approved = True
      review.save()
      return redirect(self.request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
