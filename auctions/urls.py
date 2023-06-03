from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create_listing, name="create"),
    path("by_category", views.by_category, name="by_category"),
    path("listing/<int:id>", views.listing, name="listing"),
    path("watch/<int:id>", views.watch, name="watch"),
    path("unwatch/<int:id>", views.unwatch, name="unwatch"),
    path("watchlist/", views.watchlist, name="watchlist"),
    path("comment/<int:id>", views.comment, name="comment")
]
