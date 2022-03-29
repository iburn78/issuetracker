from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import (
    ListView,
    CreateView,
    DetailView,
    UpdateView,
    DeleteView,
)
from jmespath import search
from board.models import Card, Post
from board.forms import CardForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
# use info, success, warning to make it consistent with bootstrap5
from django.contrib import messages
from django.http import Http404


def about(request):
    return render(request, 'board/about.html')


class CardListView(ListView):
    model = Card
    template_name = 'board/main.html'
    context_object_name = 'cards' # get_queryset result
    revisit = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        public_cards = Card.objects.filter(
            is_public=True).order_by('-date_created')
        context['public_cards'] = public_cards
        return context

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return super().get_queryset().filter(owner=self.request.user).filter(is_public=False).order_by('-date_created')
        else:
            if self.request.session.get('login_recommend', True) and not self.revisit:
                messages.info(
                    self.request, "IssueTracker is best to use when logged in")
                self.request.session['login_recommend'] = False
            return super().get_queryset().none()

    def post(self, request, *args, **kwargs):
        search_term = request.POST.get('search_term')
        messages.info(self.request, f"Search Keyword {search_term} entered")
        return redirect('/')

class CardSelectView(LoginRequiredMixin, CardListView): # a view for creating a new post 
    template_name = "board/card_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['card_select_for_new_post'] = True
        return context


class CardCreateView(LoginRequiredMixin, CreateView):
    model = Card
    form_class = CardForm
    template_name = 'board/card_create.html'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        # if self.request.user.is_public_card_manager:
        #     form.instance.is_public = True
        new_card = form.save(commit=False)
        new_card.save()
        form.save_m2m()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['c_u'] = 'Create'
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
        model_objects = super().get_queryset()
        selected_card = get_object_or_404(Card, id=self.kwargs.get('card_id'))
        if selected_card.is_public:
            return model_objects.filter(card__id=selected_card.id).order_by('-date_posted')
        else:
            if self.request.user.is_authenticated:
                if self.request.user == selected_card.owner:
                    return model_objects.filter(author=self.request.user).filter(card__id=selected_card.id).order_by('-date_posted')
                else:
                    raise Http404("Page not found")
            else:
                return super().get_queryset().none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['card_id'] = self.kwargs.get('card_id')
        context['card'] = get_object_or_404(Card, id=self.kwargs.get('card_id'))
        return context


class CardUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Card
    form_class = CardForm
    template_name = 'board/card_create.html'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        newcard = form.save(commit=False)
        newcard.save()
        form.save_m2m()
        return super().form_valid(form)

    def test_func(self):
        card = self.get_object()
        if self.request.user == card.owner:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['c_u'] = 'Update'
        return context

class CardDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Card
    success_url = '/'
    template_name = 'board/card_delete.html'

    def test_func(self):
        ################################
        # ADD LOGIC ON POSTS IN THE CARD
        ################################
        if self.request.user == self.get_object().owner:
            return True
        return False
