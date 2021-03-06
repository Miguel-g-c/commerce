from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Category, Auction, Bid, WatchList, Comment
from .forms import CreateForm


def index(request):
    title = 'Active listings'
    
    auctions = {}
    auctions = Auction.objects.filter(active = True).all()
    
    dict_vars = {"title": title, "auctions": auctions}

    return render(request, "auctions/index.html", dict_vars)


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required
def create_listing(request):
    if request.method == "POST":
        title = request.POST["title"]
        description = request.POST["description"]
        category_id = request.POST["category"]
        url = request.POST["article_img"]
        initial_price = request.POST["initial_price"]
        auction = Auction(title=title, description=description, initial_price=initial_price,
                          owner=request.user, category=Category.objects.get(pk=category_id), active=True,
                          article_image=url)
        auction.save()
        return HttpResponseRedirect(reverse('listed_article', args=[auction.id],))

    dict_vars = {"categories": Category.objects.all()}

    return render(request, "auctions/create_listing.html", dict_vars)


def listed_article(request, article_id):
    article = Auction.objects.get(pk=article_id)
    last_bid = Bid.objects.filter(auction=article).order_by("created").last()
    bids_count = Bid.objects.filter(auction=article).count()
    auctions_ids_in_watch_list = {}
    if request.user.is_authenticated:
        auctions_ids_in_watch_list = WatchList.objects.filter(user=request.user).values_list('auction', flat=True)

    if request.method == "POST":
        bid = Bid(user=request.user, auction=article, price=request.POST["new_bid"])
        bid.save()
        return HttpResponseRedirect(reverse("listed_article", args=[article_id]))

    dict_vars = {"article": article, "last_bid": last_bid, "bids_count": bids_count}
    dict_vars.update({"comments": Comment.objects.filter(auction=article).order_by("-created").all(),
                      "auctions_ids_in_watch_list": auctions_ids_in_watch_list})
    return render(request, "auctions/listed_article.html", dict_vars)


@login_required
def watch_list(request):
    if request.method == "POST":
        article_id = request.POST["article_id"]
        auction = Auction.objects.get(pk=article_id)
        if WatchList.objects.filter(auction=auction, user=request.user).all().first() is None:
            w = WatchList(auction=auction, user=request.user)
            w.save()
        else:
            w = WatchList.objects.get(auction=auction, user=request.user)
            w.delete()
        return HttpResponseRedirect(reverse("listed_article", args=[article_id]))

    title = 'My watchlist'
    ids = WatchList.objects.filter(user=request.user).values_list('auction', flat=True)
    auctions = Auction.objects.filter(id__in=ids)
    dict_vars = {"title": title, "auctions": auctions, "remove_article": True}

    return render(request, "auctions/index.html", dict_vars)


def close_auction(request):
    if request.method == "POST":
        article_id = request.POST["article_id"]
        auction = Auction.objects.get(pk=article_id)
        last_bid = Bid.objects.filter(auction=auction).order_by("created").last()
        if last_bid is not None:
            auction.final_buyer = last_bid.user
            auction.active = False
            auction.save()
        else:
            auction.active = False
            auction.save()
        return HttpResponseRedirect(reverse("listed_article", args=[article_id]))

@login_required
def winning_listing(request):
    title = "My buys"

    auctions = {}

    if request.user.is_authenticated:
        auctions = Auction.objects.filter(final_buyer=request.user.pk).all()
    dict_vars = {"title": title, "auctions": auctions}

    return render(request, "auctions/index.html", dict_vars)

@login_required
def my_listing(request):
    title = "My listing"

    auctions = {}

    if request.user.is_authenticated:
        auctions = Auction.objects.filter(owner=request.user.pk).all()

    dict_vars = {"title": title, "auctions": auctions}

    return render(request, "auctions/index.html", dict_vars)

def make_comment(request, article_id):
    if request.method == "POST":
        article = Auction.objects.get(pk=article_id)
        comment = Comment(user=request.user, auction=article, text=request.POST["comment_text"])
        comment.save()
        return HttpResponseRedirect(reverse("listed_article", args=[article_id]))

def categories(request):
    categories = Category.objects.all()
    dict_vars = {"categories": categories}
    return render(request, "auctions/categories.html", dict_vars)

def listed_article_by_category(request, category_id):
    category = Category.objects.get(pk=category_id)
    dict_vars = {"title": category.name,
                 "auctions": category.auctions.filter(active=True)}

    return render(request, "auctions/index.html", dict_vars)