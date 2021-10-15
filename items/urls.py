from django.urls import path, include
from . import views
from landing import views as landing_views
urlpatterns = [
    path('items/<company>/', views.CompanyListView.as_view(), name="company"),
    path('items/<company>/category/', views.CategoryListView.as_view(), name="categories"),
    path('add-to-cart/<slug>/', views.add_item_to_cart, name='add-to-cart'),
    path('upload/', views.UploadItemsView.as_view(), name='upload'),
    path('', landing_views.HomeView.as_view(), name='home')
]