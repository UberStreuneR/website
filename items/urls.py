from django.urls import path, include
from . import views
urlpatterns = [
    path('blue-things/', views.BlueThingsListView.as_view(), name="home"),
]