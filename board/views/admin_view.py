from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin 
from django.views.generic import ListView
from ..models import Report, Comment, Post, report_count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.conf import settings
import os

class ReportView(LoginRequiredMixin, ListView):
    model = Report
    template_name = 'board/reports.html'
    context_object_name = 'reports'
    paginate_by = 20 

    def get_queryset(self):
        return super().get_queryset().order_by('-date_reported')

    def get(self, request, *args, **kwargs): 
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            if request.GET.get('request_type') == 'count':
                return JsonResponse({'report_count': report_count()}, status=200)

        if request.user.is_public_card_manager:
            return super().get(request, *args, **kwargs)
        else:
            raise PermissionDenied

    def post(self, request, *args, **kwargs):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' and request.method == "POST":
            if not request.user.is_authenticated:
                return JsonResponse({}, status=400)

            request_type = request.POST.get('request_type')
            user_id = request.POST.get('user_id')
            target_id = request.POST.get('target_id')
            content = request.POST.get('report_content')
            report = Report()
            report.reporter_id = user_id
            report.content = content
            report.request_type = request_type

            if request_type == 'post': 
                report.post_id = target_id
            else:
                comment = get_object_or_404(Comment, id = target_id)
                report.post_id = comment.post.id
                report.comment_id = target_id
            report.save()
            return JsonResponse({}, status=200)
        
        else:
            if not request.user.is_public_card_manager:
                raise PermissionDenied
            ttype = request.POST.get('ttype')
            tid = request.POST.get('tid')
            if ttype == 'post': 
                get_object_or_404(Post, id = tid).delete()
            elif ttype == 'comment':
                get_object_or_404(Comment, id = tid).delete()
            elif ttype == 'report':
                get_object_or_404(Report, id = tid).delete()
            else: 
                pass
            return redirect('reports')


def exception_view(request):
    exp_file = os.path.join(settings.BASE_DIR, 'etc', 'exception_log.txt')
    if request.user.is_authenticated and request.user.is_public_card_manager:
        if request.method == "GET":
            with open(exp_file, 'r', encoding='utf-8') as exp_log:
                lines = []
                for line in exp_log:
                    lines.append(line)
                context = {'exceptions': lines, }
                return render(request, 'board/exceptions.html', context)
        elif request.method == "POST":
            if request.POST.get('request_type') == "clear": 
                open(exp_file, 'w').close()
            return redirect('exceptions')
        else:
            raise PermissionDenied
    else:
        raise PermissionDenied

def exception_counter(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.GET.get('request_type') == 'count':
            exp_file = os.path.join(settings.BASE_DIR, 'etc', 'exception_log.txt')
            with open(exp_file) as exp_log:
                return JsonResponse({'exception_count': len(exp_log.readlines())}, status=200)