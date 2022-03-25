from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from django.views.generic.edit import CreateView
from .forms import UserForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.signals import user_logged_in
from .models import User
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import FormView
from django.urls import reverse_lazy


class LoginView(FormView):
    form_class = AuthenticationForm
    template_name = 'registration/login.html'
    # success_url = reverse_lazy('home')
    # success_message = 'Welcome back %(username)s!' # A welcome message

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        print(user.role)
        if user.role != 'main':
            self.request.session['edit_mode'] = 'non-edit'
        return redirect('/')
        # return super(LoginView, self).form_valid(form)


class UserSignUp(CreateView):
    form_class = UserForm
    # success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

    #
    # def get_success_url(self):
    #     return reverse_lazy('home')

    def form_valid(self, form):
        user = form.save()
        # username = form.cleaned_data.get('username')
        # raw_password = form.cleaned_data.get('password1')
        # user = User(username=username)
        # user.set_password(raw_password)
        # user.save()
        # # user = authenticate(username=username, password=raw_password)
        login(self.request, user)
        # user = form.save()
        # login(self.request, user)
        return redirect('/')


