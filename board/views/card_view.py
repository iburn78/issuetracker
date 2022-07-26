from email.mime import base
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, resolve
from django.views.generic import (
    ListView,
    CreateView,
    DetailView,
    UpdateView,
    DeleteView,
)
from django.views import View
from ..models import Card, Post
from users.models import User
from ..forms import CardForm, CommentForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
# use info, success, warning to make it consistent with bootstrap5
from django.contrib import messages
from django.http import Http404
from django.views.static import serve
from ..tools import *
import os
from django.http import JsonResponse, HttpResponseRedirect

def about(request):
    return render(request, 'board/about.html')

class CardListView(ListView):
    model = Card
    template_name = 'board/main.html'
    context_object_name = 'cards'  # get_queryset result
    revisit = False
    card_list = False

    def post(self, request, *args, **kwargs):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' and request.method == "POST":
            card_id = request.POST.get('card_id')
            up_down = request.POST.get('up_down')
            card_to_move = get_object_or_404(Card, id=card_id)
            if card_to_move.is_public:
                card_set = Card.objects.filter(is_public=True).order_by('-card_order')
            else:
                card_set = self.get_queryset()
            card_location = 0 
            for card in card_set: 
                if str(card.id) == str(card_id):
                    break
                card_location += 1
            if (up_down == 'up' and card_location == 0) or (up_down == 'down' and card_location == len(card_set)-1):
                target_card_id = 'none'
            else: 
                if up_down == 'up':
                    target_location = card_location-1
                else: 
                    target_location = card_location+1
                temp_order = card_to_move.card_order
                card_to_move.card_order = card_set[target_location].card_order
                card_set[target_location].card_order = temp_order
                card_to_move.save()
                card_set[target_location].save()
                target_card_id = card_set[target_location].id
            return JsonResponse({"target_card_id": target_card_id}, status=200)
        else: 
            search_word = request.POST.get('search_term')
            messages.info(self.request, f"Search Keyword {search_word} entered")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        public_cards = Card.objects.filter(is_public=True).order_by('-card_order')
        context['public_cards'] = public_cards
        context['card_list'] = self.card_list
        return context

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return super().get_queryset().filter(owner=self.request.user).filter(is_public=False).order_by('-card_order')
        else:
            if self.request.session.get('login_recommend', True) and not self.revisit:
                messages.info(
                    self.request, "IssueTracker is best to use when logged in")
                self.request.session['login_recommend'] = False
            return super().get_queryset().none()



class CardSelectView(LoginRequiredMixin, CardListView):  # a view for creating a new post
    template_name = "board/card_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['card_select_for_new_post'] = True
        return context


class CardCreateView(LoginRequiredMixin, CreateView):
    model = Card
    form_class = CardForm
    template_name = 'board/card_create.html'
    def get(self, request, *args, **kwargs):
        return super().get(self, *args, **kwargs)

    def form_valid(self, form):
        form.instance.owner = self.request.user
        card_image_resize(form)
        new_card = form.save(commit=False)
        new_card.save()
        form.save_m2m()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['c_u'] = 'Create'
        context['bg_color'] = 'rgb(233, 236, 239)'
        return context


class CardContentListView(ListView):
    model = Post
    template_name = 'board/card_content.html'
    context_object_name = 'posts'
    paginate_by = 12

    def get(self, request, *args, **kwargs):
        selected_card = get_object_or_404(Card, id=kwargs.get('card_id'))
        if selected_card.is_public or self.request.user.is_authenticated:
            return super().get(request, *args, **kwargs)
        else:
            return redirect('login')

    def get_queryset(self):
        selected_card = get_object_or_404(Card, id=self.kwargs.get('card_id'))
        if selected_card.is_public:
            return Post.objects.filter(card__id=selected_card.id).order_by('-date_posted')
        else:
            if self.request.user.is_authenticated:
                if self.request.user == selected_card.owner:
                    return Post.objects.filter(author=self.request.user).filter(card__id=selected_card.id).order_by('-date_posted')
                else:
                    raise Http404("Page not found")
            else:
                return super().get_queryset().none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        card_id = self.kwargs.get('card_id')
        context['card_id'] = card_id
        context['card'] = get_object_or_404(Card, id=card_id)
        context['author_count'] = User.objects.filter(post__card_id = card_id).distinct().count()
        context['post_limit'] = POST_MAX_COUNT_TO_DELETE_A_CARD
        context['form'] = CommentForm
        return context


class CardUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Card
    form_class = CardForm
    template_name = 'board/card_create.html'

    def form_valid(self, form):
        card_image_resize(form)
        newcard = form.save(commit=False)
        newcard.save()
        form.save_m2m()
        return super().form_valid(form)

    def get_success_url(self):
        card = self.get_object()
        return reverse('card-content', args={card.id})

    def test_func(self):
        card = self.get_object()
        if self.request.user == card.owner:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['c_u'] = 'Update'
        context['bg_color'] = self.get_object().card_color
        return context

    def get_initial(self):
        initial = super().get_initial()
        return initial


class CardDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Card
    success_url = '/'
    template_name = 'board/card_delete.html'

    def test_func(self):
        if self.request.user == self.get_object().owner:
            return True
        return False
    
    def post(self, request, *args, **kwargs):
        card = self.get_object()
        post_count = card.post_set.count() 
        if post_count > POST_MAX_COUNT_TO_DELETE_A_CARD: 
            messages.warning(self.request, f"NOT DELETED!! Post count is {post_count} - not allowed to delete a card with more than {POST_MAX_COUNT_TO_DELETE_A_CARD} posts")
            return redirect('card-content', card.id)
        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        card = self.get_object()
        context['author_count'] = User.objects.filter(post__card_id = card.id).distinct().count()
        context['post_limit'] = POST_MAX_COUNT_TO_DELETE_A_CARD
        return context
    

class CardMediaView(LoginRequiredMixin, UserPassesTestMixin, View): 

    def get(self, *args, **kwargs):
        target_file = self.kwargs.get('file')
        target_dir = os.path.dirname(resolve(self.request.path_info).route)
        return serve(self.request, target_file, target_dir)

    def test_func(self):
        userid = str(self.request.user)
        res = ""
        for ch in userid:
            res += str(ord(ch))
        res = res[:7]
        if str(self.kwargs.get('file')).startswith(res):
            return True
        return False
