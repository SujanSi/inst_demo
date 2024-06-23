from django.contrib import admin
from .models import Profile,Post,Story,Like,Comment,Following
# Register your models here.


admin.site.register(Profile)
admin.site.register(Post)
admin.site.register(Story)
admin.site.register(Like)
admin.site.register(Comment)
admin.site.register(Following)