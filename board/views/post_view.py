from django.shortcuts import get_object_or_404, redirect, render
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    CreateView,
    DetailView,
    UpdateView,
    DeleteView,
)
from django.views import View

from ..models import Card, Post
from ..forms import PostForm, CommentForm
# use info, success, warning to make it consistent with bootstrap5
from django.contrib import messages
from ..tools import post_image_resize, exception_log
from django.urls import resolve
from django.views.static import serve
import os
from django.utils import timezone

def postimageview(request, *args, **kwargs): 
    template_name = "board/image_view.html"
    post = get_object_or_404(Post, id=kwargs.get('pk'))
    img_no = kwargs.get('img_no')
    context = {}
    target = ""
    if img_no == 1: target = post.image1.url
    elif img_no == 2: target = post.image2.url
    elif img_no == 3: target = post.image3.url
    elif img_no == 4: target = post.image4.url
    elif img_no == 5: target = post.image5.url
    elif img_no == 6: target = post.image6.url
    elif img_no == 7: target = post.image7.url
    else: 
        raise PermissionDenied
    context['image_url'] = target
    if post.card.is_public or request.user == post.author:
        return render(request, template_name, context)
    else: 
        raise PermissionDenied


class PostCreateView(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'board/post_create.html'

    def get(self, request, *args, **kwargs):
        selected_card = get_object_or_404(Card, id=kwargs.get('card_id'))
        if not self.request.user.is_authenticated:
            return redirect('login')

        if selected_card.is_official:
            if self.request.user.is_public_card_manager:
                return super().get(request, *args, **kwargs)
            else:
                raise PermissionDenied
        elif selected_card.is_public:
            # anybody can write in public cards
            return super().get(request, *args, **kwargs)
        else:
            if self.request.user == selected_card.owner:
                return super().get(request, *args, **kwargs)
            else:
                raise PermissionDenied

    def form_valid(self, form):
        images = []
        img_field_input = [form.cleaned_data['image1_input'], form.cleaned_data['image2_input'], form.cleaned_data['image3_input'],
                           form.cleaned_data['image4_input'], form.cleaned_data['image5_input'], form.cleaned_data['image6_input'], form.cleaned_data['image7_input']]
        
        mkeys = list(form.cleaned_data['mimage_keys'])
        mimages_input = self.request.FILES.getlist('mimages')[:7]
        for i in range(0, len(mkeys)): 
            if mkeys[i] != '_' and (img_field_input[i] == None or img_field_input[i] == False):
                img_field_input[i] = mimages_input[int(mkeys[i])-1]

        ims = list(form.cleaned_data['imgsequence'])
        img_field_input_seq_adjusted = []
        for s in ims: 
            img_field_input_seq_adjusted.append(img_field_input[int(s)-1]) 

        for img in img_field_input_seq_adjusted:
            if img != None and img != False:
                images.append(img)

        if form.cleaned_data['content'] == '' and len(images) == 0:
            messages.warning(self.request, "Enter content or at least 1 image")
            return redirect('post-create', self.kwargs.get('card_id'))

        form.instance.num_images = len(images)
        for i in range(len(images), 7):
            images.append("")
            
        [form.instance.image1, form.instance.image2, form.instance.image3, form.instance.image4,
            form.instance.image5, form.instance.image6, form.instance.image7] = images

        form.instance.author = self.request.user
        form.instance.card = get_object_or_404(Card, id=self.kwargs.get('card_id'))
        new_post = form.save(commit=False)
        new_post.save()
        form.save_m2m()
        post_image_resize(new_post)
        return redirect('card-content', self.kwargs.get('card_id'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['card'] = get_object_or_404(
            Card, id=self.kwargs.get('card_id'))
        context['num_images'] = 0
        context['image_range'] = list(range(1, 8))
        return context

    def get_initial(self):
        initial = super().get_initial()
        return initial

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'board/post_create.html'

    def form_valid(self, form):
        images = []
        img_field_input = [form.cleaned_data['image1_input'], form.cleaned_data['image2_input'], form.cleaned_data['image3_input'],
                           form.cleaned_data['image4_input'], form.cleaned_data['image5_input'], form.cleaned_data['image6_input'], form.cleaned_data['image7_input']]
        
        mkeys = list(form.cleaned_data['mimage_keys'])
        mimages_input = self.request.FILES.getlist('mimages')[:7]
        for i in range(0, len(mkeys)): 
            if mkeys[i] != '_' and (img_field_input[i] == None or img_field_input[i] == False):
                img_field_input[i] = mimages_input[int(mkeys[i])-1]

        original_images = [form.instance.image1, form.instance.image2, form.instance.image3,
                           form.instance.image4, form.instance.image5, form.instance.image6, form.instance.image7]

        for i, img in enumerate(img_field_input):
            if img_field_input[i] != original_images[i]:
                try:
                    if original_images[i].name != "":
                        original_images[i].delete()
                except:
                    text = "Exception in delete th_images - class PostUpdateView delete(): " + \
                        original_images[i].name
                    exception_log(text)

        ims = list(form.cleaned_data['imgsequence'])
        img_field_input_seq_adjusted = []
        for s in ims: 
            img_field_input_seq_adjusted.append(img_field_input[int(s)-1]) 

        for i, img in enumerate(img_field_input_seq_adjusted):
            if img != False and img != None:
                images.append(img)

        form.instance.num_images = len(images)
        if self.request.POST.get('update_date_posted')=='checked':
            form.instance.date_posted = timezone.now()
        for i in range(len(images), 7):
            images.append("")

        [form.instance.image1, form.instance.image2, form.instance.image3, form.instance.image4,
            form.instance.image5, form.instance.image6, form.instance.image7] = images

        form.instance.author = self.get_object().author
        rev_post = form.save(commit=False)
        rev_post.save()
        form.save_m2m()
        post_image_resize(rev_post)
        
        cid = self.get_object().card.id
        if rev_post.content == '' and rev_post.num_images == 0:
            messages.warning(self.request, "Post deleted - no content and no images")
            rev_post.delete()
        return redirect('card-content', cid)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.card.owner or self.request.user == post.author:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['card'] = self.get_object().card
        context['update'] = True
        num_images = self.get_object().num_images
        context['num_images'] = num_images
        simages = [self.get_object().image1s, self.get_object().image2s, self.get_object().image3s, 
            self.get_object().image4s, self.get_object().image5s, self.get_object().image6s, self.get_object().image7s]
        context['image_range'] = simages[0:num_images] + list(range(num_images+1, 8))
        return context

    def get_initial(self):
        initial = super().get_initial()
        initial['image1_input'] = self.object.image1
        initial['image2_input'] = self.object.image2
        initial['image3_input'] = self.object.image3
        initial['image4_input'] = self.object.image4
        initial['image5_input'] = self.object.image5
        initial['image6_input'] = self.object.image6
        initial['image7_input'] = self.object.image7
        return initial


class PostDetailView(DetailView): 
    model = Post
    template_name = 'board/post_detail.html'
    form_class = CommentForm
    context_object_name = 'comments'

    def get(self, request, *args, **kwargs):
        post = get_object_or_404(Post, id=self.kwargs.get('pk'))
        if post.card.is_public:
            return super().get(request, *args, **kwargs)
        else:
            if not self.request.user.is_authenticated:
                return redirect('login')
            else:
                if self.request.user == post.card.owner:
                    return super().get(request, *args, **kwargs)
                else:
                    raise PermissionDenied

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        context['post'] = post
        context['form'] = self.form_class()
        mot = ""
        if post.title.strip() != "" and post.get_preview_text().strip() !="":
            mot = post.title.strip()+": "+post.get_preview_text().strip()
        elif post.title.strip() == "":
            mot = post.get_preview_text().strip()
        else:
            pass
            #######################################
            #######################################
            #######################################
            #######################################
            #######################################
            #######################################
            #######################################
            #######################################
            #######################################
            #######################################

        context['meta_og_title'] = post.title + ": " + post.get_preview_text()
        # context['meta_og_desc'] = ''
        if post.image1s != '':
            context['meta_og_image'] = self.request.build_absolute_uri(post.image1s.url)
        return context


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.card.owner or self.request.user == post.author:
            return True
        return False

    def post(self, request, *args, **kwargs):
        card_id = self.get_object().card.id
        self.success_url = f'/card/{card_id}'
        return super().post(request, *args, **kwargs)


class PostMediaView(LoginRequiredMixin, UserPassesTestMixin, View):

    def get(self, *args, **kwargs):
        target_file = self.kwargs.get('file')
        target_dir = os.path.dirname(resolve(self.request.path_info).route)
        return serve(self.request, target_file, target_dir)

    def test_func(self):
        userid = str(self.request.user)
        res = ""
        for ch in userid:
            res += str(ord(ch))
        res = res[:7]
        if str(self.kwargs.get('file')).startswith(res):
            return True
        return False
