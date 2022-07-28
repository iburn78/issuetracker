from datetime import datetime
from django.shortcuts import get_object_or_404, render
from django.core.exceptions import PermissionDenied
from django.views.generic import ListView
from django.views import View
from ..models import Post, Comment
from ..forms import CommentForm
from django.http import JsonResponse

class CommentListView(ListView): 
    model = Comment
    context_object_name = 'comments'
    template_name = 'board/comment_list.html'
    paginate_by = 7 
    form_class = CommentForm

    def get(self, request, *args, **kwargs):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' and request.method == "GET":
            self.object_list = self.get_queryset()
            context = self.get_context_data()
            return render(request, self.template_name, context, status=200)
    
    def get_queryset(self):
        return Comment.objects.filter(post__id=self.kwargs.get('pk')).order_by('-date_posted')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = get_object_or_404(Post, id=self.kwargs.get('pk'))
        context['form'] = self.form_class()
        return context


class CommentCreateView(View):
    model = Comment
    form_class = CommentForm

    def post(self, request, *args, **kwargs):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' and request.method == "POST":
            if not request.user.is_authenticated:
                return JsonResponse({}, status=400)
            content = request.POST.get('content')
            if content == "": 
                return JsonResponse({}, status=400)
            cform = CommentForm()
            cform.instance.author = request.user
            cform.instance.post_id = self.kwargs.get('pk')
            cform.instance.content = content
            new_comment = cform.save(commit=False)
            new_comment.save()
            return JsonResponse({}, status=200)


class CommentMgmtView(View):
    model = Comment
    form_class = CommentForm

    def get(self, request, *args, **kwargs):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' and request.method == "GET":
            comment = get_object_or_404(Comment, id=self.kwargs.get('pk'))
            return JsonResponse({"content": comment.content}, status=200)

    def post(self, request, *args, **kwargs):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' and request.method == "POST":
            if not request.user.is_authenticated:
                return JsonResponse({}, status=400)

            request_type = request.POST.get('request_type')
            comment = get_object_or_404(Comment, id=self.kwargs.get('pk'))

            if request_type == 'update': 
                if request.user == comment.author:
                    comment.content = request.POST.get('content')
                    # comment.date_posted = datetime.now()
                    comment.save()
                    return JsonResponse({}, status=200)
                else:
                    raise PermissionDenied

            elif request_type == 'delete': 
                if request.user == comment.author:
                    comment.delete()
                    return JsonResponse({}, status=200)
                else:
                    raise PermissionDenied

            else:
                return JsonResponse({}, status=400)
    
