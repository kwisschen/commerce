from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from decimal import Decimal


class User(AbstractUser):
    pass


class Category(models.Model):
    category_name = models.CharField(max_length=50)

    def __str__(self):
        return self.category_name


# make sure that the Bid model is above the Listing model for ForeignKey 'price' to work
class Bid(models.Model):
    bid = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="user_bids")

    def __str__(self):
        return self.bid


class Listing(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=1000)
    price = models.ForeignKey(Bid, on_delete=models.CASCADE, blank=True, null=True, related_name="listing_bid")
    is_active = models.BooleanField(default=True)
    image_url = models.CharField(max_length=1000)
    poster = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="posted_listings")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, related_name="listing_category")
    watched_by = models.ManyToManyField(User, blank=True, null=True, related_name="watched_listings")

    def __str__(self):
        return self.name


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="user_comments")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, blank=True, null=True, related_name="listing_comments")
    message = models.CharField(max_length=300, default='')
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.author}'s comment on {self.listing}"

