from django.urls import path
from inst import views
from django.conf.urls.static import static 
from django.conf import settings

app_name = 'inst'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_View, name="login_View"),
    path('signup/', views.signup_view, name="signup_view"),
    path('logout/', views.logout_view, name="logout_view"),

    path('update-profile/', views.update_profile, name='update_profile'),

    path('profile/', views.profile_view, name="profile_view"),
    path('create_post/', views.create_post, name='create_post'),


    path('change-password/', views.change_password, name='change_password'),


    path('story', views.story, name='story'),
    path('stories/', views.view_all_stories, name='view_all_stories'),
    
    path('add_comment/<int:post_id>/', views.add_comment, name='add_comment'),

    path('like/<int:post_id>/', views.toggle_like, name='toggle_like'),

    path('post/<int:post_id>/likes/', views.post_likes, name='post_likes'),

    path("notifications/", views.notifications, name="notifications"),

    path('profile/<str:username>/', views.user_profile_view, name='user_profile'),

    path('accept-follow-request/<int:request_id>/', views.accept_follow_request, name='accept_follow_request'),
    path('reject-follow-request/<int:request_id>/', views.reject_follow_request, name='reject_follow_request'),

    path('profile/<str:username>/followers/', views.followers_list, name='followers_list'),
    path('profile/<str:username>/following/', views.following_list, name='following_list'),

    path('messages/', views.message_list, name='messages'),
    path("chat/<str:username>/", views.chat_view, name="chat"),  # Chat with a user


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 
