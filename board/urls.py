from django.urls import path
from .views.base_view import *
from .views.card_view import *
from .views.post_view import *
from .views.comment_view import *
from .views.admin_view import *
from django.conf import settings
from django.views.generic import RedirectView
from .tools import *
from os.path import join


urlpatterns = [
    path('test/', test, name='test'),
    path('', CardListView.as_view(), name='main'),
    path('card_list/', CardListView.as_view(template_name="board/card_list.html"), name='card-list'),
    path('card_select/', CardSelectView.as_view(), name='card-select'),
    path('about/', about, name='about'),
    path('new_card/', CardCreateView.as_view(), name='card-create'),
    path('card/<int:card_id>/', CardContentListView.as_view(), name='card-content'),
    path('card/<int:pk>/update/', CardUpdateView.as_view(), name='card-update'),
    path('card/<int:pk>/delete/', CardDeleteView.as_view(), name='card-delete'),
    path('card/<int:card_id>/new_post/', PostCreateView.as_view(), name='post-create'),
    path('post_delete/<int:pk>/', PostDeleteView.as_view(), name='post-delete'),
    path('post_update/<int:pk>/', PostUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('post/<int:pk>/images', PostImageView.as_view(), name='post-images'),
    path('post/<int:pk>/images/<int:img_no>/', postimageview, name='postimage-view'),
    path('reports/', ReportView.as_view(), name = 'reports'),
    path('exceptions/', exception_view, name = 'exceptions'),
    path('search/', search, name = 'search'),
    path('mylikes/', SearchView_MyLikes.as_view(), name = 'mylikes'),
    path('aposts/<int:pk>/', SearchView_AuthorPosts.as_view(), name = 'author-posts'),
    path('tposts/<int:pk>/', SearchView_TagPosts.as_view(), name = 'tag-posts'),

    path('favicon.ico', RedirectView.as_view(url=settings.STATIC_URL+'board/IssueTracker_Logo.png')),
    path(join('media', POST_UPLOADED_IMGS, '<str:file>'), PostMediaView.as_view(), name='media-view'),
    path(join('media', POST_UPLOADED_IMGS_RESIZED, '<str:file>'), PostMediaView.as_view(), name='media-view'),
    path(join('media', CARD_UPLOADED_IMGS, '<str:file>'), CardMediaView.as_view(), name='media-view'),
    
    path('api/vote/', vote, name='vote'),
    path('api/card/move/', CardListView.as_view(), name='card-move'),
    path('api/post/move/', CardSelectView.as_view(), name='post-mp-mgmt'),
    path('api/post/<int:pk>/comment_list/', CommentListView.as_view(), name='comment-list'),
    path('api/comment/<int:pk>/replies_list/', RepliesListView.as_view(), name='replies-list'),
    path('api/post/<int:pk>/comment_new/', CommentCreateView.as_view(), name='comment-new'),
    path('api/comment/<int:pk>/reply_new/', ReplyCreateView.as_view(), name='reply-new'),
    path('api/comment/<int:pk>/', CommentMgmtView.as_view(), name='comment-mgmt'),
    path('api/comment/counter/', comment_counter, name='comment-counter'),
    path('api/reply/counter/', reply_counter, name='reply-counter'),
    path('api/report/counter/', ReportView.as_view(), name = 'report-counter'),
    path('api/exception/counter/', exception_counter, name = 'exception-counter'),
    path('api/user/modechange/', user_mode_change, name = 'user-mode-change'),
    path('api/card_content_post_page/<int:card_id>/<int:post_id>', CardContentListView.as_view(), name = 'card-content-post-page'),

    path('api/search/path/', search_path, name = 'search-path'),
    path('api/search/card/', SearchView_Card.as_view(), name = 'search-card'),
    path('api/search/post/', SearchView_Post.as_view(), name = 'search-post'),
    path('api/search/author/', SearchView_Author.as_view(), name = 'search-author'),
    
    path('api/increase-post-view/', IncreasePostViewCount.as_view(), name='increase-post-view'),

]
