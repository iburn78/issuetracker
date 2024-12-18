from django.shortcuts import get_object_or_404, render
from django.core.exceptions import PermissionDenied
from django.views.generic import ListView
from django.views import View
from ..models import Post, Comment
from ..forms import CommentForm
from django.http import JsonResponse
from django.utils import timezone

def comment_counter(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' and request.method == "GET":
        post_id = request.GET.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        commentscount = post.comment_set.filter(reply_to = None).count()
        return JsonResponse({"allrepliescount": post.comment_set.count(), "commentscount": commentscount}, status = 200)

def reply_counter(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' and request.method == "GET":
        comment_id = request.GET.get('comment_id')
        comment = get_object_or_404(Comment, id=comment_id)
        repliescount = comment.comment_set.count()
        return JsonResponse({"allrepliescount": comment.post.comment_set.count(), "repliescount": repliescount, "post_id": comment.post.id}, status = 200)

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
        return Comment.objects.filter(post__id=self.kwargs.get('pk')).filter(reply_to = None).order_by('-date_posted')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['linked_obj'] = get_object_or_404(Post, id=self.kwargs.get('pk'))
        context['form'] = self.form_class()
        context['CR'] = 'comment'
        context['CRs'] = 'comments'
        return context

class RepliesListView(ListView): 
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
        return Comment.objects.filter(reply_to__id=self.kwargs.get('pk')).order_by('-date_posted')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['linked_obj'] = get_object_or_404(Comment, id=self.kwargs.get('pk'))
        context['form'] = self.form_class()
        context['CR'] = 'reply'
        context['CRs'] = 'replies'
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

class ReplyCreateView(View):
    model = Comment
    form_class = CommentForm

    def post(self, request, *args, **kwargs):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' and request.method == "POST":
            if not request.user.is_authenticated:
                return JsonResponse({}, status=400)
            content = request.POST.get('content')
            rtr_target_id = request.POST.get('rtr_target_id')
            if content == "": 
                return JsonResponse({}, status=400)
            cform = CommentForm()
            cform.instance.author = request.user
            cform.instance.reply_to_id = self.kwargs.get('pk')
            reply_to_comment = get_object_or_404(Comment, id = self.kwargs.get('pk'))
            cform.instance.post_id = reply_to_comment.post.id
            cform.instance.content = content
            if rtr_target_id != '':
                cform.instance.rtr_id = rtr_target_id
            new_comment = cform.save(commit=False)
            new_comment.save()
            return JsonResponse({}, status=200)


class CommentMgmtView(View):
    model = Comment
    form_class = CommentForm

    def get(self, request, *args, **kwargs):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' and request.method == "GET":
            comment = get_object_or_404(Comment, id=self.kwargs.get('pk'))
            contentbrief = comment.content[:100]
            date_posted = timezone.localtime(comment.date_posted).strftime("%y-%m-%d %H:%M")
            return JsonResponse({"content": comment.content,
            "contentbrief": contentbrief,             
            "date_posted": date_posted,             
            }, status=200)

    def post(self, request, *args, **kwargs):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' and request.method == "POST":
            if not request.user.is_authenticated:
                return JsonResponse({}, status=400)

            request_type = request.POST.get('request_type')
            comment = get_object_or_404(Comment, id=self.kwargs.get('pk'))

            if request_type == 'update': 
                if request.user == comment.author:
                    comment.content = request.POST.get('content')
                    # comment.date_posted = timezone.now()
                    comment.save()
                    return JsonResponse({}, status=200)
                else:
                    raise PermissionDenied

            elif request_type == 'delete': 
                if request.user == comment.author or request.user.is_public_card_manager:
                    comment.delete()
                    return JsonResponse({}, status=200)
                else:
                    raise PermissionDenied

            else:
                return JsonResponse({}, status=400)
    

class IncreasePostViewCount(View):
    """Handle AJAX requests to increment Post view count."""
    def post(self, request, *args, **kwargs):
        post_id = request.POST.get('post_id')
        if post_id:
            post = get_object_or_404(Post, id=post_id)

            # Session logic to ensure only one increment per session
            viewed_posts = request.session.get('viewed_posts', [])
            if post.id not in viewed_posts:
                post.increase_view_count()  # Increment the Post view count
                viewed_posts.append(post.id)
                request.session['viewed_posts'] = viewed_posts
                request.session.set_expiry(86400)  # Optional: 24-hour expiry
            
            # Return the updated view count
            return JsonResponse({'success': True, 'view_count': post.view_count, 'cview_count': post.card.view_count})
        
        return JsonResponse({'success': False, 'error': 'Invalid post ID'}, status=400)