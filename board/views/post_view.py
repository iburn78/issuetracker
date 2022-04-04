from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    ListView,
    CreateView,
    DetailView,
    UpdateView,
    DeleteView,
)
from board.models import Card, Post
from board.forms import PostForm
from django.contrib import messages


class PostCreateView(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'board/post_create.html'

    def get(self, request, *args, **kwargs):
        selected_card = get_object_or_404(Card, id=kwargs.get('card_id'))
        if not self.request.user.is_authenticated:
            return redirect('login')

        if selected_card.is_public:
            if self.request.user.is_public_card_manager:
                return super().get(request, *args, **kwargs)
            else:
                raise PermissionDenied
        else:
            if self.request.user == selected_card.owner:
                return super().get(request, *args, **kwargs)
            else:
                raise PermissionDenied

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.card = get_object_or_404(
            Card, id=self.kwargs.get('card_id'))
        new_post = form.save(commit=False)
        new_post.save()
        form.save_m2m()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['card'] = get_object_or_404(Card, id=self.kwargs.get('card_id'))
        return context


# class PostDetailView(DetailView): # DO I NEED THIS?
#     model = Post
#     template_name = 'board/post_detail.html'

#     def get(self, request, *args, **kwargs):
#         post = get_object_or_404(Post, id=kwargs.get('pk'))
#         if post.card.is_public:
#             return super().get(request, *args, **kwargs)
#         else:
#             if not self.request.user.is_authenticated:
#                 return redirect('login')
#             else:
#                 if self.request.user == post.card.owner:
#                     return super().get(request, *args, **kwargs)
#                 else:
#                     raise PermissionDenied

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         return context


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

    def post(self, request, *args, **kwargs):
        card_id = self.kwargs.get('card_id')
        self.success_url = f'/card/{card_id}'
        return super().post(request, *args, **kwargs)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'board/post_create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        newpost = form.save(commit=False)
        newpost.save()
        form.save_m2m()
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['update'] = True
        return context
