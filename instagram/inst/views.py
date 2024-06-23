from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout 
from .forms import SignupForm, LoginForm,StoryForm,PostForm
from django.contrib import messages
from .models import Post
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required
# Create your views here.

@login_required
def home(request):
    feeds = Post.objects.all()
    return render(request, 'inst/index.html', {'feeds': feeds})

def login_View(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('inst:home')
            else:
                # Return an 'invalid login' error message.
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
        
    return render(request, 'inst/login.html', {'form': form})

def signup_view(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully!')
            return redirect('inst:login_View')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = SignupForm()

    return render(request, 'inst/signup.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('inst:login')

@login_required
def profile(request):
    return render(request,'inst/profile.html')

@login_required
def story(request):
    if request.method=="POST":
        form = StoryForm(request.POST, request.FILES)
        if form.is_valid():
            new_story = form.save(commit = False)
            new_story.author = request.user.profile
            new_story.created_at = timezone.now()
            new_story.expire_at = timezone.now + timedelta(hours=24)
            new_story.save()
            return redirect('inst:index')
    else:
        form = StoryForm()

    return render(request,'inst/story.html',{'form':form})

@login_required
def post(request):
    return render(request,'inst/post.html')
