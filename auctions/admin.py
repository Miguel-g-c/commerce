from django.contrib import admin
from .models import Category, User, Auction, Bid, Comment, WatchList

# Register your models here.
admin.site.register(Category)
admin.site.register(User)
admin.site.register(Auction)
admin.site.register(Bid)
admin.site.register(Comment)
admin.site.register(WatchList)