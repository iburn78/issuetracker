from re import search
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import resolve
from django.views.generic import ListView
from ..models import Card, Post, Comment
from users.models import User
from django.http import JsonResponse
from django.core import serializers
from django.core.exceptions import PermissionDenied
from django.db.models import Q, Count

def test(request):
    return render(request, 'board/test.html')

def about(request):
    return render(request, 'board/about.html')

def user_mode_change(request):
    if not request.user.is_authenticated:
        return PermissionDenied
    request.user.is_in_private_mode = not request.user.is_in_private_mode
    request.user.save()
    return redirect('main')

def vote(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' and request.method == "POST":
        object_id = request.POST.get('object_id')
        up_down = request.POST.get('up_down')
        object_type = request.POST.get('object')
        if object_type == 'post': 
            object = get_object_or_404(Post, id=object_id)
        elif object_type == 'comment':
            object = get_object_or_404(Comment, id=object_id)
        else: 
            return JsonResponse({"result": "failure"}, status = 400)
        fill_status = 'neither'
        if up_down == 'up':
            if object.likes.all().filter(id=request.user.id).exists():
                object.likes.remove(request.user)
            else:
                object.likes.add(request.user)
                fill_status = 'up'
                if object.dislikes.all().filter(id=request.user.id).exists():
                    object.dislikes.remove(request.user)
        elif up_down == 'down':
            if object.dislikes.all().filter(id=request.user.id).exists():
                object.dislikes.remove(request.user)
            else:
                object.dislikes.add(request.user)
                fill_status = 'down'
                if object.likes.all().filter(id=request.user.id).exists():
                    object.likes.remove(request.user)
        else:
            pass
        ser_instance = serializers.serialize('json', [object])
        return JsonResponse({"instance": ser_instance, "fill_status": fill_status}, status=200)
    return JsonResponse({"result": "failure"}, status = 400)


def search_path(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' and request.method == "POST":
        path = resolve(request.POST.get('path'))
        if path.url_name == "card-content":
            cid = path.kwargs['card_id']
            return JsonResponse({"url_name": path.url_name, "cid": cid}, status=200)
        else: 
            return JsonResponse({"url_name": path.url_name,}, status=200)

class SearchView_Card(ListView):
    model = Card
    paginate_by = 3
    template_name = 'board/search_card.html'
    context_object_name = 'cards'

    def get(self, request, *args, **kwargs):
        res = super().get(request, *args, **kwargs).render().content.decode("utf-8")
        return JsonResponse({"res": res}, status=200)

    def get_queryset(self):
        search_term = self.request.GET.get('search_term')
        if self.request.user.is_authenticated and self.request.user.is_in_private_mode:
            return Card.objects.filter(Q(owner=self.request.user) & Q(is_public=False) & (Q(title__icontains=search_term) | Q(desc__icontains=search_term))).distinct().order_by('-date_created')
        else: 
            return Card.objects.filter(Q(is_public=True) & (Q(title__icontains=search_term) | Q(desc__icontains=search_term))).distinct().order_by('-date_created')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_term'] = self.request.GET.get('search_term')
        return context

class SearchView_Post(ListView):
    model = Post
    paginate_by = 3
    template_name = 'board/search_post.html'
    context_object_name = 'posts'

    def get(self, request, *args, **kwargs):
        res = super().get(request, *args, **kwargs).render().content.decode("utf-8")
        return JsonResponse({"res": res}, status=200)

    def get_queryset(self):
        search_term = self.request.GET.get('search_term')
        cid = self.request.GET.get('cid')
        if self.request.user.is_authenticated and self.request.user.is_in_private_mode:
            if cid == None:
                return Post.objects.filter(Q(author=self.request.user) & Q(card__is_public=False) & Q(content__icontains=search_term)).distinct().order_by('-date_posted')
            else: 
                return Post.objects.filter(Q(card_id = cid) & Q(author=self.request.user) & Q(card__is_public=False) & Q(content__icontains=search_term)).distinct().order_by('-date_posted')
        else: 
            if cid == None:
                return Post.objects.filter(Q(card__is_public=True) & Q(content__icontains=search_term)).distinct().order_by('-date_posted')
            else: 
                return Post.objects.filter(Q(card_id = cid) & Q(card__is_public=True) & Q(content__icontains=search_term)).distinct().order_by('-date_posted')

    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_term'] = self.request.GET.get('search_term')
        cid = self.request.GET.get('cid')
        if cid != None:
            context['cid'] = cid
        else: 
            context['cid'] = ''
        context['target_model'] = "post"
        return context

class SearchView_Tag(SearchView_Post):
    def get_queryset(self):
        search_term = self.request.GET.get('search_term')
        cid = self.request.GET.get('cid')
        if self.request.user.is_authenticated and self.request.user.is_in_private_mode:
            if cid == None:
                return Post.objects.filter(Q(author=self.request.user) & Q(card__is_public=False) & Q(tags__name=search_term)).distinct().order_by('-date_posted')
            else: 
                return Post.objects.filter(Q(card_id = cid) & Q(author=self.request.user) & Q(card__is_public=False) & Q(tags__name=search_term)).distinct().order_by('-date_posted')
        else: 
            if cid == None:
                return Post.objects.filter(Q(card__is_public=True) & Q(tags__name=search_term)).distinct().order_by('-date_posted')
            else: 
                return Post.objects.filter(Q(card_id = cid) & Q(card__is_public=True) & Q(tags__name=search_term)).distinct().order_by('-date_posted')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['target_model'] = "tag"
        return context

class SearchView_MyLikes(SearchView_Post):
    def get_queryset(self):
        if self.request.user.is_authenticated and not self.request.user.is_in_private_mode: 
            pset = self.request.user.liked_post_set
            search_term = self.request.GET.get('search_term')
            cid = self.request.GET.get('cid')
            if search_term == None and cid == None: 
                return pset.all().distinct().order_by('-date_posted')
            elif search_term == None and cid != None: 
                return pset.filter(card_id = cid).distinct().order_by('-date_posted')
            elif search_term != None and cid == None: 
                return pset.filter(content__icontains = search_term).distinct().order_by('-date_posted')
            else: 
                return pset.filter(card_id = cid).filter(content__icontains = search_term).distinct().order_by('-date_posted')
        else: 
            return Post.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['target_model'] = "mylikes"
        return context

class SearchView_Author(ListView):
    model = User
    paginate_by = 3
    template_name = 'board/search_author.html'
    context_object_name = 'authors'

    def get(self, request, *args, **kwargs):
        res = super().get(request, *args, **kwargs).render().content.decode("utf-8")
        return JsonResponse({"res": res}, status=200)

    def get_queryset(self):
        search_term = self.request.GET.get('search_term')
        return User.objects.annotate(num_posts=Count('post', filter=Q(post__card__is_public=True))).filter(Q(username__icontains=search_term) & Q(num_posts__gt=0)).distinct().order_by('username')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_term'] = self.request.GET.get('search_term')
        return context
