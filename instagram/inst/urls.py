from django.urls import path
from inst import views
from django.conf.urls.static import static 
from django.conf import settings

app_name = 'inst'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_View, name="login_View"),
    path('signup/', views.signup_view, name="signup_view"),
    path('profile/', views.profile, name="profile"),
    path('story', views.story, name='story'),
    

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 
