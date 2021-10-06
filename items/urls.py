from django.urls import path, include
from . import views
urlpatterns = [
    path('<category>/', views.CategoryListView.as_view(), name="categories"),
    path('<category>/<subcategory>/', views.ItemList.as_view(), name="subcategories")
]