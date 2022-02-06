from django.shortcuts import render
from django.views.generic import (
    ListView,
    CreateView,
    DetailView,
    UpdateView,
    DeleteView,
)
from board.models import Card, Post
from board.forms import CardForm
# from django.contrib import messages

# Create your views here.
def about(request):
    return render(request, 'board/about.html')

class CardCreateView(CreateView):
    model = Card
    form_class = CardForm
    template_name = 'board/card_create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        new_card = form.save(commit=False)
        new_card.save()
        form.save_m2m()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['main_color'] = 'bg-red-100'
        # messages.warning(self.request, "First Message")
        # messages.info(self.request, "Second Message")
        return context

class CardListView(ListView):
    model = Card
    template_name = 'board/index.html'
    context_object_name = 'cards'   # context['cards'] = Card.objects.all() 
    # however, assigning context directly does not work with pagination
    paginate_by = 12

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['main_color'] = 'bg-red-100'
        return context

    def get_queryset(self):
        return super().get_queryset().order_by('-date_created')


class CardContentListView(ListView):
    model = Post
    template_name = 'board/card_content.html'
    context_object_name = 'posts'   
    paginate_by = 12

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['main_color'] = 'bg-yellow-100'
        return context

    def get_queryset(self):
        return super().get_queryset().order_by('-date_posted')
