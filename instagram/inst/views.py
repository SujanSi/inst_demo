from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout 
from .forms import SignupForm, LoginForm,StoryForm,PostForm,ProfileUpdateForm,CommentForm
from django.contrib import messages
from .models import Post,Profile,Story,Like,FollowRequest,Following,Message
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.db.models import Max
from django.db.models import Exists, OuterRef
# Create your views here.
@login_required
def home(request):
    user_profile, created = Profile.objects.get_or_create(user=request.user)
    # Fetch all posts and annotate with whether the logged-in user has liked each post
    feeds = Post.objects.prefetch_related('comments', 'comments__user').annotate(
        liked_by_user=Exists(
            Like.objects.filter(user=request.user.profile, post=OuterRef('id'))
        )
    ).order_by('-pub_date')
    
    # Get the logged-in user's Profile instance
    user_profile = Profile.objects.get(user=request.user)
    
    # Get the latest story for the logged-in user
    user_story = Story.objects.filter(author=user_profile).order_by('-created_at').first()
    
    # Get the latest story for each other author
    latest_story_per_author = Story.objects.exclude(author=user_profile).values('author').annotate(latest_created_at=Max('created_at'))
    
    # Fetch the stories based on the latest created_at for each author
    other_stories = Story.objects.filter(
        author__in=[story['author'] for story in latest_story_per_author],
        created_at__in=[story['latest_created_at'] for story in latest_story_per_author]
    ).order_by('author', '-created_at')
    
    # Combine the logged-in user's story with the other stories
    stories = [user_story] if user_story else []
    stories.extend(other_stories)

    return render(request, 'inst/index.html', {'feeds': feeds, 'stories': stories})

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
    return redirect('inst:login_View')


@login_required
def story(request):
    if request.method=="POST":
        form = StoryForm(request.POST, request.FILES)
        if form.is_valid():
            new_story = form.save(commit = False)
            new_story.author = request.user.profile
            new_story.created_at = timezone.now()
            new_story.expires_at = timezone.now() + timedelta(hours=24)
            new_story.save()
            return redirect('inst:home')
    else:
        form = StoryForm()

    return render(request,'inst/story.html',{'form':form})
@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user.profile  # Set the current user's profile as the author
            post.save()
            messages.success(request, 'Your post has been uploaded successfully!')
            return redirect('inst:profile_view') 
        else:
            messages.error(request, 'There was an error uploading your post.')
    else:
        form = PostForm()

    return render(request, 'inst/post.html', {'form': form})



@login_required
def update_profile(request):
    print("Rendering update profile page")
    profile = request.user.profile
    
    if request.method == 'POST': 
        print("POST method triggered")
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        print(request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('inst:profile_view')
        else:
            print(form.errors)
    else:
        form = ProfileUpdateForm(instance=profile)
    
    return render(request, 'inst/update_profile.html', {'form': form})


def profile_view(request):
    # Get or create the profile for the logged-in user
    profile, created = Profile.objects.get_or_create(user=request.user)

    # Set default values if bio or profile_pic is null/empty
    if not profile.bio:
        profile.bio = "No bio added yet."
    if not profile.profile_pic:
        profile.profile_pic = "profile_pic/default_profile.jpg"  # Use a placeholder image path

    posts = Post.objects.filter(author=profile)

     # Include follower and following counts
    followers_count = profile.followers_count  # Dynamically calculated property
    following_count = profile.following_count  # Dynamically calculated property

# Get the list of followers and following
    followers_list = Following.objects.filter(following_user=profile).select_related('follower')
    following_list = Following.objects.filter(follower=profile).select_related('following_user')
    context = {
        'profile': profile,
        'posts': posts,
        'followers_count': followers_count,
        'following_count': following_count,
        'followers_list': followers_list,  # List of profiles following this user
        'following_list': following_list,  # List of profiles this user is following
    }

    return render(request, 'inst/profile.html', context)



@login_required
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        user = request.user

        # Check if the current password is correct
        if not user.check_password(current_password):
            messages.error(request, 'Current password is incorrect.')
            return redirect('inst:change_password')

        # Check if new password and confirm password match
        if new_password != confirm_password:
            messages.error(request, 'New password and Confirm password do not match.')
            return redirect('inst:change_password')

        # Update the user's password
        user.set_password(new_password)
        user.save()

        # Keep the user logged in after password change
        update_session_auth_hash(request, user)
        messages.success(request, 'Your password has been successfully changed!')
        return redirect('inst:profile_view')  # Redirect to the profile page or any other desired page

    return render(request, 'inst/password.html')



def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    print("Post fetched:", post)
    if request.method == "POST":
        print("POST data:", request.POST)
        form = CommentForm(request.POST)
        if form.is_valid():
            print("Form is valid")
            comment = form.save(commit=False)
            comment.user = request.user.profile  # Ensure this is correct
            comment.post = post
            comment.save()
            return redirect('inst:home')
        else:
            print("Form errors:", form.errors)
    return redirect('inst:home')


@login_required
def toggle_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user_profile = request.user.profile  # Assuming a `Profile` model exists linked to the user.

    # Check if the user has already liked the post
    like, created = Like.objects.get_or_create(user=user_profile, post=post)

    if not created:
        # If the like already exists, remove it (unlike)
        like.delete()

    # Redirect back to the same page
    return redirect('inst:home')

@login_required
def post_likes(request, post_id):
    # Get the post and its likes
    post = get_object_or_404(Post, id=post_id)
    likes = post.like_set.select_related('user')

    # Pass the likes to the template
    return render(request, 'inst/post_likes.html', {'post': post, 'likes': likes})


@login_required
def view_all_stories(request):
    # Fetch all stories, ordered by creation time (latest first)
    stories = Story.objects.select_related('author').order_by('-created_at')

    # Get all stories for the logged-in user
    user_stories = stories.filter(author=request.user.profile)
    # Get all other stories except the logged-in user's
    other_stories = stories.exclude(author=request.user.profile)

    context = {
        "user_stories": user_stories,
        "other_stories": other_stories,
    }
    return render(request, "inst/view_all_stories.html", context)

@login_required
def notifications(request):
    # Get all pending follow requests for the logged-in user
    follow_requests = FollowRequest.objects.filter(receiver=request.user, status="pending").order_by("-created_at")

    print(follow_requests)  # Debugging: Print the queryset to ensure it's not empty

    return render(
        request,
        "inst/notifications.html",
        {
            "follow_requests": follow_requests,
        },
    )
from django.urls import reverse
from django.http import HttpResponseRedirect
@login_required
def user_profile_view(request, username):
    # Get the user whose profile is being visited
    user = get_object_or_404(User, username=username)

    # Get or create the profile for that user
    profile, created = Profile.objects.get_or_create(user=user)

     # Handle follow action if the form is submitted
    if request.method == "POST":
        # Check if the logged-in user is not trying to follow themselves
        if request.user != user:
            # Create a follow request
            FollowRequest.objects.create(sender=request.user, receiver=user, status="pending")
        
        # Redirect back to the same profile page to update the button
        return HttpResponseRedirect(reverse('inst:user_profile', args=[username]))

    # Get all posts by the user
    posts = Post.objects.filter(author=profile)

    # Calculate the follower and following counts dynamically
    followers_count = Following.objects.filter(following_user=profile).count()
    following_count = Following.objects.filter(follower=profile).count()

    # Check if the logged-in user has sent a follow request to this user
    follow_request_sent = FollowRequest.objects.filter(
        sender=request.user,
        receiver=user,
        status="pending"
    ).exists()

    # Check if the logged-in user is already following this user
    is_following = Following.objects.filter(
        follower__user=request.user,
        following_user=profile
    ).exists()

    # Logic for showing the follow button
    show_follow_button = request.user != user and not follow_request_sent and not is_following

    context = {
        'profile': profile,
        'posts': posts,
        'followers_count': followers_count,
        'following_count': following_count,
        'follow_request_sent': follow_request_sent,
        'is_following': is_following,
        'show_follow_button': show_follow_button,
    }

    return render(request, 'inst/user_profile.html', context)

@login_required
def accept_follow_request(request, request_id):
    follow_request = get_object_or_404(FollowRequest, id=request_id, receiver=request.user)
    follow_request.status = "accepted"
    follow_request.save()

    # Create the following relationship
    Following.objects.get_or_create(
        follower=follow_request.sender.profile,
        following_user=follow_request.receiver.profile
    )

    return redirect('inst:notifications')

@login_required
def reject_follow_request(request, request_id):
    follow_request = get_object_or_404(FollowRequest, id=request_id, receiver=request.user)
    follow_request.status = "rejected"
    follow_request.save()

    return redirect('inst:notifications')



@login_required
def followers_list(request, username):
    # Get the profile of the user whose followers you want to see
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=user)

    # Get the list of followers (Profiles that are following the current profile)
    followers = Following.objects.filter(following_user=profile).select_related('follower')

    context = {
        'profile': profile,
        'followers': [follower.follower for follower in followers],
    }
    return render(request, 'inst/followers_list.html', context)


@login_required
def following_list(request, username):
    # Get the profile of the user whose following list you want to see
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=user)

    # Get the list of profiles this user is following
    following = Following.objects.filter(follower=profile).select_related('following_user')

    context = {
        'profile': profile,
        'following': [f.following_user for f in following],
    }
    return render(request, 'inst/following_list.html', context)



def message_list(request):
    # Get logged-in user's profile
    user_profile = get_object_or_404(Profile, user=request.user)

    # Get mutual followers (users who follow each other)
    following = Following.objects.filter(follower=user_profile).values_list('following_user', flat=True)
    followers = Following.objects.filter(following_user=user_profile).values_list('follower', flat=True)

    # Find users who are in both lists (mutual followers)
    mutual_followers = Profile.objects.filter(id__in=set(following) & set(followers))

        # Create a list of mutual followers with their profile picture
    mutual_followers_data = [
        {
            "username": user.user.username,
            "profile_pic": user.profile_pic.url if user.profile_pic else "/static/default-profile.png"
        }
        for user in mutual_followers
    ]


    context = {
        'mutual_followers': mutual_followers_data,
        
    }
    return render(request, 'inst/message_list.html', context)


@login_required
def chat_view(request, username):
    other_user = get_object_or_404(Profile, user__username=username)
    messages = Message.objects.filter(sender=request.user.profile, receiver=other_user) | \
               Message.objects.filter(sender=other_user, receiver=request.user.profile)
    messages = messages.order_by("timestamp")

    return render(request, "inst/chat.html", {
        "other_user": other_user,
        "messages": messages
    })
