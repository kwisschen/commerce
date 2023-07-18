from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from decimal import Decimal
from django.shortcuts import get_object_or_404

from .models import User, Category, Listing, Comment, Bid


def index(request):
    active_listings = Listing.objects.filter(is_active=True)
    all_categories = Category.objects.all() # select all categories from Category table
    return render(request, "auctions/index.html", {
        "listings": active_listings,
        "categories": all_categories,
    })


def by_category(request):
    if request.method == "POST":
        selected_category = request.POST["category"] # "name" attr from select tag in index.html
        category = Category.objects.get(category_name=selected_category)
        active_listings = Listing.objects.filter(is_active=True, category=category)
        all_categories = Category.objects.all()
        return render(request, "auctions/index.html", {
            "listings": active_listings,
            "categories": all_categories,
            "selected_category": selected_category  # Add selected_category to the context
        })


def create_listing(request):
    if request.method == "GET":
        all_categories = Category.objects.all()
        return render(request, "auctions/create.html", {
            "categories": all_categories,
        })
    elif request.method == "POST":
        # get data from our form
        name = request.POST["name"]
        description = request.POST["description"] # from 'name' attr in input tag
        price = request.POST["price"]
        image_url = request.POST["imageurl"]
        current_user = request.user
        category = request.POST["category"]
        # need to access entire record of data that can actually go into Category table
        category_data = Category.objects.get(category_name=category)

        # Create and save new Bid object
        bid = Bid(
            bid = price,
            user= current_user
        )
        bid.save()

        # Create and save new Listing object
        new_listing = Listing(
            name=name, # left-side vars are vars in Listing model, right-side vars are local
            description=description,
            price=bid,
            image_url=image_url,
            poster=current_user,
            category=category_data
        )
        new_listing.save()
        return HttpResponseRedirect(reverse('index'))


def listing(request, id):
    listing_data = Listing.objects.get(pk=id)
    watchlisted = request.user in listing_data.watched_by.all()
    listing_comments = Comment.objects.filter(listing=listing_data) # grabs 'listing' field from model of current listing
    is_poster = request.user.username == listing_data.poster.username
    return render(request, "auctions/listing.html", {
        "listing": listing_data,
        "watchlisted": watchlisted,
        "comments": listing_comments,
        "poster": is_poster
    })


def watchlist(request):
    current_user = request.user
    watched_listings = current_user.watched_listings.all() # the related name from Listing model
    return render(request, "auctions/watchlist.html", {
        "listings": watched_listings,
    })


def watch(request, id):
    listing_data = Listing.objects.get(pk=id)
    current_user = request.user
    listing_data.watched_by.add(current_user)
    # redirect to "listing/<int:id>" url with arg as a tuple
    return HttpResponseRedirect(reverse("listing", args=(id, )))


def unwatch(request, id):
    current_user = request.user
    listing_data = Listing.objects.get(pk=id)
    listing_data.watched_by.remove(current_user)
    return HttpResponseRedirect(reverse("listing", args=(id, )))



def bid(request, id):
    new_bid = request.POST.get("new_bid")
    listing_data = get_object_or_404(Listing, pk=id)
    watchlisted = request.user in listing_data.watched_by.all()
    listing_comments = Comment.objects.filter(listing=listing_data)
    is_poster = request.user.username == listing_data.poster.username

    if new_bid:
        new_bid_value = Decimal(new_bid)
        if listing_data.price is None or new_bid_value > listing_data.price.bid:
            latest_bid = Bid.objects.create(bid=new_bid_value, user=request.user)
            listing_data.price = latest_bid
            listing_data.save()
            return render(request, "auctions/listing.html", {
                "listing": listing_data,
                "message": "your bid has been successfully placed.",
                "updated": True,
                "poster": is_poster,
                "watchlisted": watchlisted,
                "comments": listing_comments
            })

    return render(request, "auctions/listing.html", {
        "listing": listing_data,
        "message": "Your bid should be greater than the current bid.",
        "updated": False,
        "poster": is_poster,
        "watchlisted": watchlisted,
        "comments": listing_comments
    })


def comment(request, id):
    current_user = request.user
    listing_data = Listing.objects.get(pk=id)
    message = request.POST["new_comment"]

    new_comment = Comment(
        author = current_user,
        listing = listing_data,
        message = message
    )
    new_comment.save()
    return HttpResponseRedirect(reverse("listing", args=(id, )))


def close_auction(request, id):
    listing_data = Listing.objects.get(pk=id)
    watchlisted = request.user in listing_data.watched_by.all()
    listing_comments = Comment.objects.filter(listing=listing_data)
    is_poster = request.user.username == listing_data.poster.username
    listing_data.is_active = False
    listing_data.save()
    return render(request, "auctions/listing.html", {
        "listing": listing_data,
        "watchlisted": watchlisted,
        "comments": listing_comments,
        "poster": is_poster,
        "updated": True,
        "message": "your auction has been closed successfully. Congratulations!"
    })


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
