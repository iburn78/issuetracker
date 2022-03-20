from django.shortcuts import render, get_object_or_404
from django.views.generic import (
    ListView,
    CreateView,
    DetailView,
    UpdateView,
    DeleteView,
)
from board.models import Card, Post
from board.forms import CardForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages

# Create your views here.


def about(request):
    return render(request, 'board/about.html')


class CardCreateView(LoginRequiredMixin, CreateView):
    model = Card
    form_class = CardForm
    template_name = 'board/card_create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        if self.request.user.is_public_card_manager:
            form.instance.is_public = True
        new_card = form.save(commit=False)
        new_card.save()
        form.save_m2m()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class CardListView(ListView):
    model = Card
    template_name = 'board/index.html'
    context_object_name = 'cards'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        public_cards = Card.objects.filter(is_public=True).order_by('-date_created')
        context['public_cards'] = public_cards
        return context

    def get_queryset(self):
        if self.request.user.is_authenticated:
<<<<<<< HEAD
            return super().get_queryset().filter(author = self.request.user).order_by('-date_created')
        else:
            return None
=======
            return super().get_queryset().filter(author=self.request.user).order_by('-date_created')
        else:
            return Card.objects.none()
>>>>>>> a87610dc9e3606de290e0c7bed6e1bda1fa2bb2b


class CardContentListView(ListView):
    model = Post
    template_name = 'board/card_content.html'
    context_object_name = 'posts'
    paginate_by = 12

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['card_id'] = self.kwargs.get('pk')
        return context

    def get_queryset(self):
<<<<<<< HEAD
        model_objects= super().get_queryset()
        if self.request.user.is_authenticated:
            Not public:

Logged in 
-	My card: my post filter -> show
-	Not my card: 404

Not logged-in: redirect to login

Public:
	Filter the post under the card and show -> later, more authentication might be required
if self.request.user == get_object_or_404(Card, id=self.kwargs.get('card_id')).author:

        if self.request.user.is_authenticated:
            queryset = model_objects.filter(author = self.request.user).filter(card__id = self.kwargs.get('card_id'))
        else: 

        return queryset.order_by('-date_posted')
=======
        model_objects = super().get_queryset()
        queryset = model_objects.filter(author=self.request.user).filter(
            card__id=self.kwargs.get('card_id'))
        return queryset.order_by('-date_posted')

    def test_func(self):
        if self.request.user == get_object_or_404(Card, id=self.kwargs.get('card_id')).author:
            return True
        return False
>>>>>>> a87610dc9e3606de290e0c7bed6e1bda1fa2bb2b
