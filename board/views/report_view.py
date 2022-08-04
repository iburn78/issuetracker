from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin 
from django.views.generic import ListView
from ..models import Report
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.conf import settings
import os

class ReportView(LoginRequiredMixin, ListView):
    model = Report
    template_name = 'board/reports.html'
    context_object_name = 'reports'

    def get(self, request, *args, **kwargs): 
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

            if request_type == 'post': 
                report.post_id = target_id
            elif request_type == 'comment': 
                report.comment_id = target_id
            report.save()
            return JsonResponse({}, status=200)

def exception_view(request):
  if request.user.is_authenticated and request.user.is_public_card_manager:
    exp_file = os.path.join(settings.BASE_DIR, 'etc/exception_log.txt')
    with open(exp_file) as exp_log:
        lines = exp_log.readlines
        context = {'exceptions': lines, }
        return render(request, 'board/exceptions.html', context)
  else:
    raise PermissionDenied
