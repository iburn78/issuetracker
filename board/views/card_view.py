from django.shortcuts import render, get_object_or_404, redirect
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
from django.http import Http404

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
            return super().get_queryset().filter(author = self.request.user).order_by('-date_created')
        else:
            return None


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
        model_objects= super().get_queryset()
        selected_card = get_object_or_404(Card, id=self.kwargs.get('card_id'))
        if selected_card.is_public:
            return model_objects.filter(author = self.request.user).filter(card__id = selected_card.id)
        else:
            if self.request.user.is_authenticated:
                if self.request.user == selected_card.author:
                    return model_objects.filter(author = self.request.user).filter(card__id = selected_card.id)
                else:
                    raise Http404("Page not found")
            else:
                return redirect('login')






