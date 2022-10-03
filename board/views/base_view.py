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
from django.contrib.auth.mixins import LoginRequiredMixin
from django.template.defaulttags import register



def test(request):
    if request.method == "POST": 
        files = request.FILES.getlist('image')
        print(files)
        file = request.FILES.get('image0')
        print(file)
    return render(request, 'board/test.html')

def about(request):
    return render(request, 'board/about.html')

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

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


def search(request):
    context = {}
    search_term = request.GET.get('search_term') 
    if search_term != None:
        context['search_term'] = search_term
        context['search_requested'] = 'requested'
    else: 
        context['search_term'] = ''
        context['search_requested'] = 'not'
    return render(request, 'board/search.html', context)


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
    paginate_by = 4
    template_name = 'board/search_card.html'
    context_object_name = 'cards'

    def get(self, request, *args, **kwargs):
        res = super().get(request, *args, **kwargs).render().content.decode("utf-8")
        return JsonResponse({"res": res, "count": len(self.get_queryset())}, status=200)

    def get_queryset(self):
        search_term = self.request.GET.get('search_term')
        if self.request.user.is_authenticated and self.request.user.is_in_private_mode:
            return Card.objects.filter(Q(owner=self.request.user) & Q(is_public=False) & (Q(title__icontains=search_term) | Q(desc__icontains=search_term))).distinct().order_by('-card_order')
        else: 
            return Card.objects.filter(Q(is_public=True) & (Q(title__icontains=search_term) | Q(desc__icontains=search_term))).distinct().order_by('-card_order')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_term'] = self.request.GET.get('search_term')
        return context


class SearchView_Post(ListView):
    model = Post
    paginate_by = 6
    template_name = 'board/search_post.html'
    context_object_name = 'objects'

    def get(self, request, *args, **kwargs):
        res = super().get(request, *args, **kwargs).render().content.decode("utf-8")
        return JsonResponse({"res": res, "count": len(self.get_queryset())}, status=200)
    
    def get_queryset(self):
        search_model = self.request.GET.get('search_model')
        search_term = self.request.GET.get('search_term')
        cid = self.request.GET.get('cid')

        if search_model == "post":
            if self.request.user.is_authenticated and self.request.user.is_in_private_mode:
                if cid == None:
                    return Post.objects.filter(Q(author=self.request.user) & Q(card__is_public=False) & (Q(title__icontains=search_term) | Q(content__icontains=search_term))).distinct().order_by('-date_posted')
                else: 
                    return Post.objects.filter(Q(card_id = cid) & Q(author=self.request.user) & Q(card__is_public=False) & (Q(title__icontains=search_term) | Q(content__icontains=search_term))).distinct().order_by('-date_posted')
            else: 
                if cid == None:
                    return Post.objects.filter(Q(card__is_public=True) & (Q(title__icontains=search_term) | Q(content__icontains=search_term))).distinct().order_by('-date_posted')
                else: 
                    return Post.objects.filter(Q(card_id = cid) & Q(card__is_public=True) & (Q(title__icontains=search_term) | Q(content__icontains=search_term))).distinct().order_by('-date_posted')

        elif search_model == "mylikes":
            if self.request.user.is_authenticated and not self.request.user.is_in_private_mode: 
                pset = self.request.user.liked_post_set
                if cid == None: 
                    return pset.filter(Q(title__icontains=search_term) | Q(content__icontains=search_term)).distinct().order_by('-date_posted')
                else: 
                    return pset.filter(card_id = cid).filter(Q(title__icontains=search_term) | Q(content__icontains=search_term)).distinct().order_by('-date_posted')
            else: 
                return Post.objects.none()

        elif search_model == "taggedpost":
            if self.request.user.is_authenticated and self.request.user.is_in_private_mode:
                if cid == None:
                    return Post.objects.filter(Q(author=self.request.user) & Q(card__is_public=False)).filter(Q(tags__name__iexact=search_term)).distinct().order_by('-date_posted')
                else:
                    return Post.objects.filter(Q(card_id = cid) & Q(author=self.request.user) & Q(card__is_public=False)).filter(Q(tags__name__iexact=search_term)).distinct().order_by('-date_posted')
            else: 
                if cid == None:
                    return Post.objects.filter(Q(card__is_public=True)).filter(Q(tags__name__iexact=search_term)).distinct().order_by('-date_posted')
                else:
                    return Post.objects.filter(Q(card_id = cid) & Q(card__is_public=True)).filter(Q(tags__name__iexact=search_term)).distinct().order_by('-date_posted')

        elif search_model == "tag":
            self.paginate_by = 15
            if self.request.user.is_authenticated and self.request.user.is_in_private_mode:
                if cid == None:
                    return Post.tags.filter(Q(post__author=self.request.user) & Q(post__card__is_public=False)).filter(Q(name__icontains=search_term)).distinct().order_by('name')
                else:
                    return Post.tags.filter(Q(post__card_id = cid) & Q(post__author=self.request.user) & Q(post__card__is_public=False)).filter(Q(name__icontains=search_term)).distinct().order_by('name')
            else: 
                if cid == None:
                    return Post.tags.filter(Q(post__card__is_public=True)).filter(Q(name__icontains=search_term)).distinct().order_by('name')
                else:
                    return Post.tags.filter(Q(post__card_id = cid) & Q(post__card__is_public=True)).filter(Q(name__icontains=search_term)).distinct().order_by('name')
        
        else:
            return Post.objects.none()


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_model = self.request.GET.get('search_model')
        context['search_model'] = search_model
        context['search_term'] = self.request.GET.get('search_term')
        cid = self.request.GET.get('cid')
        if cid != None:
            context['cid'] = cid
        else: 
            context['cid'] = ''
        return context


class SearchView_Author(ListView):
    model = User
    paginate_by = 10
    template_name = 'board/search_author.html'
    context_object_name = 'authors'

    def get(self, request, *args, **kwargs):
        res = super().get(request, *args, **kwargs).render().content.decode("utf-8")
        return JsonResponse({"res": res, "count": len(self.get_queryset())}, status=200)

    def get_queryset(self):
        if self.request.user.is_in_private_mode: 
            return User.objects.none()
        search_term = self.request.GET.get('search_term')
        cid = self.request.GET.get('cid')
        if cid != None:
            return User.objects.annotate(num_posts=Count('post', filter=(Q(post__card__is_public=True) & Q(post__card_id=cid)))).filter(Q(username__icontains=search_term) & Q(num_posts__gt=0)).distinct().order_by('username')
        else: 
            return User.objects.annotate(num_posts=Count('post', filter=Q(post__card__is_public=True))).filter(Q(username__icontains=search_term) & Q(num_posts__gt=0)).distinct().order_by('username')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_term'] = self.request.GET.get('search_term')
        cid = self.request.GET.get('cid')
        qs = self.get_queryset()
        num_post = {}
        if cid != None:
            context['cid'] = cid
            for u in qs:
                num_post[u.id] = u.post_set.filter(Q(card_id=cid) & Q(card__is_public=True)).count()
        else: 
            context['cid'] = ''
            for u in qs:
                num_post[u.id] = u.post_set.filter(Q(card__is_public=True)).count()
        context['num_post'] = num_post
        return context


class SearchView_MyLikes(LoginRequiredMixin, ListView):
    model = Post
    paginate_by = 20
    template_name = 'board/post_list.html'
    context_object_name = 'posts'
    
    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.is_in_private_mode:
            self.request.user.is_in_private_mode = False
            self.request.user.save()
        return self.request.user.liked_post_set.distinct().order_by('-date_posted')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_target'] = 'mylikes'
        return context


class SearchView_AuthorPosts(ListView):
    model = Post
    paginate_by = 20
    template_name = 'board/post_list.html'
    context_object_name = 'posts'
    
    def get_queryset(self):
        aid = self.kwargs.get('pk')
        cid = self.request.GET.get('cid')
        if self.request.user.is_authenticated and self.request.user.is_in_private_mode:
            self.request.user.is_in_private_mode = False
            self.request.user.save()
        if cid != None and cid != '':
            return User.objects.filter(id=aid).get().post_set.filter(Q(card__is_public=True) & Q(card_id=cid)).distinct().order_by('-date_posted')
        else: 
            return User.objects.filter(id=aid).get().post_set.filter(card__is_public=True).distinct().order_by('-date_posted')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        aid = self.kwargs.get('pk')
        cid = self.request.GET.get('cid')
        if cid != None and cid != '':
            context['cid'] = cid
            context['scope'] = Card.objects.get(id=cid)
        else: 
            context['scope'] = 'public cards'
        context['search_target'] = 'authorposts'
        context['authorname'] = User.objects.filter(id=aid).get().username
        return context


class SearchView_TagPosts(ListView):
    model = Post
    paginate_by = 20
    template_name = 'board/post_list.html'
    context_object_name = 'posts'
    
    def get_queryset(self):
        tid = self.kwargs.get('pk')
        cid = self.request.GET.get('cid')
        if self.request.user.is_authenticated and self.request.user.is_in_private_mode:
            if cid == None or cid=='':
                return Post.objects.filter(Q(author=self.request.user) & Q(card__is_public=False)).filter(Q(tags__id=tid)).distinct().order_by('-date_posted')
            else:
                return Post.objects.filter(Q(card_id = cid) & Q(author=self.request.user) & Q(card__is_public=False)).filter(Q(tags__id=tid)).distinct().order_by('-date_posted')
        else: 
            if cid == None or cid=='':
                return Post.objects.filter(Q(card__is_public=True)).filter(Q(tags__id=tid)).distinct().order_by('-date_posted')
            else:
                return Post.objects.filter(Q(card_id = cid) & Q(card__is_public=True)).filter(Q(tags__id=tid)).distinct().order_by('-date_posted')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tid = self.kwargs.get('pk')
        cid = self.request.GET.get('cid')
        if cid != None and cid != '':
            context['cid'] = cid
            card = Card.objects.get(id=cid)
            if card.is_public: 
                if self.request.user.is_authenticated and self.request.user.is_in_private_mode:
                    self.request.user.is_in_private_mode = False
                    self.request.user.save()
            else:
                if card.owner == self.request.user:
                    if self.request.user.is_authenticated and not self.request.user.is_in_private_mode:
                        self.request.user.is_in_private_mode = True
                        self.request.user.save()
                else: 
                    raise PermissionDenied
            context['scope'] = Card.objects.get(id=cid).title
        else: 
            if self.request.user.is_authenticated and self.request.user.is_in_private_mode:
                context['scope'] = 'my cards'
            else:
                context['scope'] = 'public cards'
        context['search_target'] = 'tagposts'
        context['tagname'] = Post.tags.get(id=tid)
        return context