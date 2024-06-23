from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=255,blank=True,null=True)
    profile_pic = models.ImageField(upload_to='profile_pic/', blank=True)

    def __str__(self):
        return self.user.username


class Post(models.Model):
  author = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='posts')
  caption = models.TextField(max_length=255, blank=True)
  image = models.ImageField(upload_to='posts/')
  pub_date = models.DateTimeField(auto_now_add=True)

  class Meta:
    ordering = ['-pub_date']

  def __str__(self):
    return self.caption

class Story(models.Model):
    author = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='stories')
    image = models.ImageField(upload_to='stories/')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"Story by {self.author.user.username} created at {self.created_at}"
    

class Like(models.Model):
  user = models.ForeignKey(Profile, on_delete=models.CASCADE)
  post = models.ForeignKey(Post, on_delete=models.CASCADE)

  class Meta:
    unique_together = (
       ('user', 'post'),
       )

  def __str__(self):
    return f"{self.user.user.username} likes {self.post.author.user.username}'s post"
  
class Comment(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.user.username} comments: '{self.text}' on {self.post.caption}"
    

class Following(models.Model):
  follower = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='following')
  following_user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='followers')

  class Meta:
    unique_together = (('follower', 'following_user'),)

  def __str__(self):
    return f"{self.follower.user.username} follows {self.following_user.user.username}"