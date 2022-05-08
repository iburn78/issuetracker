from re import A
from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    ListView,
    CreateView,
    DetailView,
    UpdateView,
    DeleteView,
)
from board.models import Card, Post
from board.forms import PostForm
from django.contrib import messages
from board.tools import post_image_resize

class PostCreateView(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'board/post_create.html'

    def get(self, request, *args, **kwargs):

        selected_card = get_object_or_404(Card, id=kwargs.get('card_id'))
        if not self.request.user.is_authenticated:
            return redirect('login')

        if selected_card.is_public:
            if self.request.user.is_public_card_manager:
                return super().get(request, *args, **kwargs)
            else:
                raise PermissionDenied
        else:
            if self.request.user == selected_card.owner:
                return super().get(request, *args, **kwargs)
            else:
                raise PermissionDenied

    def form_valid(self, form):
        images = []
        img_field_input = [form.cleaned_data['image1_input'], form.cleaned_data['image2_input'], form.cleaned_data['image3_input'], form.cleaned_data['image4_input'], form.cleaned_data['image5_input'], form.cleaned_data['image6_input'], form.cleaned_data['image7_input']]
        for img in img_field_input:
            if img != None: images.append(img)
        form.instance.num_images = len(images)
        for i in range(len(images), 7):
            images.append("")
        [form.instance.image1, form.instance.image2, form.instance.image3, form.instance.image4, form.instance.image5, form.instance.image6, form.instance.image7] = images
        # [form.instance.image1s, form.instance.image2s, form.instance.image3s, form.instance.image4s, form.instance.image5s, form.instance.image6s, form.instance.image7s] = images
        form.instance.author = self.request.user
        form.instance.card = get_object_or_404(
            Card, id=self.kwargs.get('card_id'))
        new_post = form.save(commit=False)
        new_post.save()
        form.save_m2m()
        # th_images = [form.instance.image1s, form.instance.image2s, form.instance.image3s, form.instance.image4s, form.instance.image5s, form.instance.image6s, form.instance.image7s]
        # for i in range(0, form.instance.num_images):
        #     post_image_resize(th_images[i])
        post_image_resize(new_post)
        return redirect(self.get_success_url())
        # return super().form_valid(form) # this saves the form again
    
    def get_success_url(self) -> str:
        card_id = self.kwargs.get('card_id')
        return f'/card/{card_id}'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['card'] = get_object_or_404(Card, id=self.kwargs.get('card_id'))
        context['num_images'] = 1
        return context


# class PostDetailView(DetailView): # DO I NEED THIS?
#     model = Post
#     template_name = 'board/post_detail.html'

#     def get(self, request, *args, **kwargs):
#         post = get_object_or_404(Post, id=kwargs.get('pk'))
#         if post.card.is_public:
#             return super().get(request, *args, **kwargs)
#         else:
#             if not self.request.user.is_authenticated:
#                 return redirect('login')
#             else:
#                 if self.request.user == post.card.owner:
#                     return super().get(request, *args, **kwargs)
#                 else:
#                     raise PermissionDenied

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         return context


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

    def post(self, request, *args, **kwargs):
        card_id = self.kwargs.get('card_id')
        self.success_url = f'/card/{card_id}'
        return super().post(request, *args, **kwargs)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'board/post_create.html'

    def form_valid(self, form):
        images = []
        # timages = []
        # new_timages_index = []
        img_field_input = [form.cleaned_data['image1_input'], form.cleaned_data['image2_input'], form.cleaned_data['image3_input'], form.cleaned_data['image4_input'], form.cleaned_data['image5_input'], form.cleaned_data['image6_input'], form.cleaned_data['image7_input']]
        original_images = [form.instance.image1, form.instance.image2, form.instance.image3, form.instance.image4, form.instance.image5, form.instance.image6, form.instance.image7]
        # th_images = [form.instance.image1s, form.instance.image2s, form.instance.image3s, form.instance.image4s, form.instance.image5s, form.instance.image6s, form.instance.image7s]
        for i, img in enumerate(img_field_input):
            if img_field_input[i] != original_images[i]:
                try:
                    original_images[i].delete()
                    # th_images[i].delete()
                except:
                    print("Exception in delete images - class PostUpdateView: ", i)

            if img != False and img != None: 
                images.append(img)
                # if img_field_input[i] != original_images[i]:
                #     timages.append(img)
                #     new_timages_index.append(len(timages)-1)
                # else:
                #     timages.append(th_images[i])
        form.instance.num_images = len(images)
        for i in range(len(images), 7):
            images.append("")
            # timages.append("")
        [form.instance.image1, form.instance.image2, form.instance.image3, form.instance.image4, form.instance.image5, form.instance.image6, form.instance.image7] = images
        # [form.instance.image1s, form.instance.image2s, form.instance.image3s, form.instance.image4s, form.instance.image5s, form.instance.image6s, form.instance.image7s] = timages
        
        form.instance.author = self.request.user
        rev_post = form.save(commit=False)
        rev_post.save()
        form.save_m2m()
        # th_images = [form.instance.image1s, form.instance.image2s, form.instance.image3s, form.instance.image4s, form.instance.image5s, form.instance.image6s, form.instance.image7s]
        # for i in new_timages_index: 
        #     post_image_resize(th_images[i])
        post_image_resize(rev_post)
        return redirect(self.get_success_url())
        # return super().form_valid(form) # this saves the form again

    def get_success_url(self) -> str:
        card_id = self.kwargs.get('card_id')
        return f'/card/{card_id}'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['update'] = True
        context['num_images'] = max(1, self.get_object().num_images)
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
