from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class Auction(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField()
    initial_price = models.FloatField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="my_actions")
    final_buyer = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,
                                    related_name="bought_actions")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="auctions")
    active = models.BooleanField()
    created = models.DateTimeField(auto_now_add=True)
    article_image = models.URLField()

    def __str__(self):
        return f"title:{self.title}, " \
               f"owner: {self.owner}, " \
               f"active:{self.active}"

    @property
    def last_bid(self):
        return Bid.objects.filter(auction=self).order_by("created").last()



class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="bids")
    created = models.DateTimeField(auto_now_add=True)
    price = models.FloatField()

    def __str__(self):
        return f"user:{self.user.username}, " \
               f"auction: {self.auction.title}, " \
               f"price:{self.price}"


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="comments")
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"user:{self.user.username}, " \
               f"auction: {self.auction.title}, " \
               f"comment: {self.text} "


class WatchList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watch_lists")
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="watch_lists")