from django.urls import path, include
from . import views
from landing import views as landing_views
urlpatterns = [
    path('items/<company>/', views.CompanyListView.as_view(), name="company"),
    path('items/<company>/category/', views.CategoryListView.as_view(), name="categories"),
    path('search/', views.SearchView.as_view(), name='search'),
    path('items/<company>/<article>/', views.ItemView.as_view(), name='item'),
    path('add-to-cart/<slug>/', views.add_item_to_cart, name='add-to-cart'),
    path('ajax-add-to-cart/<slug>/', views.ajax_add_to_cart, name='ajax-add-to-cart'),
    path('ajax-add-single-to-cart/<slug>/', views.ajax_add_single_to_cart, name='ajax-add-single-to-cart'),
    path('remove-from-cart/<slug>/', views.remove_item_from_cart, name='remove-from-cart'),
    path('ajax-remove-single-from-cart/<slug>/', views.ajax_remove_single_from_cart, name='ajax-remove-single-from-cart'),
    path('remove-single-from-cart/<slug>/', views.remove_single_item_from_cart, name='remove-single-from-cart'),
    path('discard-cart/', views.discard_cart, name='discard'),
    path('upload/', views.UploadItemsView.as_view(), name='upload'),
    path('download/', views.Download.as_view(), name='download'),
    path('', landing_views.HomeView.as_view(), name='home')
]