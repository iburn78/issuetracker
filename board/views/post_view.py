from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, resolve
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.files.base import ContentFile
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
from django.views.static import serve
import os
from django.utils import timezone
from PIL import Image
from django.utils.html import strip_tags
from django.http import HttpResponseRedirect
from django.db import transaction


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
    elif img_no == 8: target = post.image8.url
    elif img_no == 9: target = post.image9.url
    elif img_no == 10: target = post.image10.url     
    else: 
        raise PermissionDenied
    context['post'] = post
    context['image_url'] = target
    context['meta_og_title'] = post.title.strip()
    context['meta_og_desc'] = strip_tags(post.get_preview_text()).strip()
    context['meta_og_image'] = request.build_absolute_uri(target)
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
                           form.cleaned_data['image4_input'], form.cleaned_data['image5_input'], form.cleaned_data['image6_input'], 
                           form.cleaned_data['image7_input'], form.cleaned_data['image8_input'], form.cleaned_data['image9_input'], form.cleaned_data['image10_input']]
        
        mkeys = list(form.cleaned_data['mimage_keys'])
        mimages_input = self.request.FILES.getlist('mimages')[:10] # multiple file selection does not perform image validation

        AN = {'A': 1, 'B': 2, 'C':3, 'D':4, 'E':5, 'F':6, 'G':7, 'H':8, 'I':9, 'J':10}
        for i in range(0, len(mkeys)): 
            if mkeys[i].isdigit():
                l = int(mkeys[i])
                if l == 0: 
                    l = 10
                img = mimages_input[l-1]
                try: 
                    Image.open(img)
                    images.append(img)
                except:
                    pass
            elif mkeys[i].isupper():
                images.append(img_field_input[AN[mkeys[i]]-1])
            else: 
                pass

        if form.cleaned_data['content'] == '' and len(images) == 0:
            messages.warning(self.request, "Enter content or at least 1 image")
            return redirect('post-create', self.kwargs.get('card_id'))

        form.instance.num_images = len(images)
        for i in range(len(images), 10):
            images.append("")
            
        # [form.instance.image1, form.instance.image2, form.instance.image3, form.instance.image4,
        #     form.instance.image5, form.instance.image6, form.instance.image7, form.instance.image8, form.instance.image9, form.instance.image10] = images

        # Start atomic transaction
        with transaction.atomic():  # Start atomic block to ensure all actions are done atomically
            try:
                # Rename and save images with simple names (image1, image2, etc.)
                # for idx, img in enumerate(images):
                #     if img:  # Only process if img is not empty
                #         _, ext = os.path.splitext(img.name)
                #         filename = f"image{idx+1}{ext}"
                #         img_content = ContentFile(img.read())  # Read the image content
                #         getattr(form.instance, f'image{idx+1}').save(filename, img_content)

                [form.instance.image1, form.instance.image2, form.instance.image3, form.instance.image4,
                    form.instance.image5, form.instance.image6, form.instance.image7, form.instance.image8, form.instance.image9, form.instance.image10] = images

                form.instance.author = self.request.user
                if self.request.POST.get('html_or_text')=='html':
                    form.instance.is_html = True;
                else:
                    form.instance.is_html = False;
                form.instance.card = get_object_or_404(Card, id=self.kwargs.get('card_id'))
                new_post = form.save(commit=False)
                new_post.save()
                form.save_m2m()
        
                post_image_resize(new_post)
                return redirect('card-content', self.kwargs.get('card_id'))

            except Exception as e:
                exception_log(f"Error in form_valid transaction: {e}")
                messages.warning(self.request, "There was an error processing your request.")
                return redirect('post-create', self.kwargs.get('card_id'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['card'] = get_object_or_404(Card, id=self.kwargs.get('card_id'))
        context['num_images'] = 0
        context['image_range'] = list(range(1, 11))  
        context['html_or_text'] = ""
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
                           form.cleaned_data['image4_input'], form.cleaned_data['image5_input'], form.cleaned_data['image6_input'], 
                           form.cleaned_data['image7_input'], form.cleaned_data['image8_input'], form.cleaned_data['image9_input'], form.cleaned_data['image10_input']]

        original_images = [form.instance.image1, form.instance.image2, form.instance.image3,
                           form.instance.image4, form.instance.image5, form.instance.image6, 
                           form.instance.image7, form.instance.image8, form.instance.image9, form.instance.image10]
        
        mkeys = list(form.cleaned_data['mimage_keys'])
        mimages_input = self.request.FILES.getlist('mimages')[:10]

        AN = {'A': 1, 'B': 2, 'C':3, 'D':4, 'E':5, 'F':6, 'G':7, 'H':8, 'I':9, 'J':10}
        for i in range(0, len(mkeys)): 
            if mkeys[i].isdigit():
                l = int(mkeys[i])
                if l == 0: 
                    l = 10
                img = mimages_input[l-1]
                try: 
                    Image.open(img)
                    images.append(img)
                except:
                    pass
            elif mkeys[i].isupper():
                images.append(img_field_input[AN[mkeys[i]]-1])
            else: 
                pass

        form.instance.num_images = len(images)
    
        if self.request.POST.get('update_date_posted')=='update_date':
            form.instance.date_posted = timezone.now()
        for i in range(len(images), 10):
            images.append("")

        # [form.instance.image1, form.instance.image2, form.instance.image3, form.instance.image4,
        #     form.instance.image5, form.instance.image6, form.instance.image7, form.instance.image8, form.instance.image9, form.instance.image10] = images

        img_content_list = []        
        for img in images:
            if img:  # Only process if img is not empty
                img_content_list.append(ContentFile(img.read())) 

        # Start atomic transaction
        with transaction.atomic():  # Start atomic block to ensure all actions are done atomically
            try:
                # Delete prevously saved images from disk
                for img in original_images:
                    try: 
                        if img and img.name:
                            img.delete(save=False)
                    except Exception as e: 
                        exception_log(f"Error deleting image {img.name} in post {self.get_object().id}: {e}")

                # Rename and save images with simple names (image1, image2, etc.)
                for idx, img in enumerate(images):
                    if img:  # Only process if img is not empty
                        _, ext = os.path.splitext(img.name)
                        filename = f"image{idx+1}{ext}"
                        getattr(form.instance, f'image{idx+1}').save(filename, img_content_list[idx])
        
                form.instance.author = self.get_object().author
                if self.request.POST.get('html_or_text')=='html':
                    form.instance.is_html = True;
                else:
                    form.instance.is_html = False;
                rev_post = form.save(commit=False)
                rev_post.save()
                form.save_m2m()

                post_image_resize(rev_post)
        
                cid = self.get_object().card.id
                if rev_post.content == '' and rev_post.num_images == 0:
                    messages.warning(self.request, "Post deleted - no content and no images")
                    rev_post.delete()
                    return redirect('card-content', cid)

                print(reverse('card-content-post-page', args={cid, rev_post.id}))

                return HttpResponseRedirect(reverse('card-content-post-page', kwargs={'card_id': cid, 'post_id': rev_post.id}))

            except Exception as e:
                # Rollback if there's an error in any part of the transaction
                exception_log(f"Error in form_valid transaction: {e}")
                messages.warning(self.request, "There was an error processing your request.")
                return redirect('post-update', self.get_object().id)


    def test_func(self):
        post = self.get_object()
        if self.request.user == post.card.owner or self.request.user == post.author:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        context['card'] = post.card
        context['update'] = True
        num_images = post.num_images
        context['num_images'] = num_images
        simages = [post.image1s, post.image2s, post.image3s, 
            post.image4s, post.image5s, post.image6s, post.image7s, post.image8s, post.image9s, post.image10s]
        context['image_range'] = simages[0:num_images] + list(range(num_images+1, 11))  
        if post.is_html:
            context['html_or_text'] = 'checked'
        else:
            context['html_or_text'] = ''
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
        initial['image8_input'] = self.object.image8
        initial['image9_input'] = self.object.image9
        initial['image10_input'] = self.object.image10
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
        context['meta_og_title'] = post.title.strip()
        context['meta_og_desc'] = strip_tags(post.get_preview_text()).strip()
        if post.image1s != '':
            context['meta_og_image'] = self.request.build_absolute_uri(post.image1s.url)
        return context


class PostImageView(DetailView): 
    model = Post
    template_name = 'board/post_images.html'
    context_object_name = 'post'

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
        images = [post.image1s, post.image2s, post.image3s, post.image4s, post.image5s, post.image6s, post.image7s, post.image8s, post.image9s, post.image10s]
        context['images'] = images[0:post.num_images]
        context['meta_og_title'] = post.title.strip()
        context['meta_og_desc'] = strip_tags(post.get_preview_text()).strip()
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
