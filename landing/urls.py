from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.HomeView.as_view(), name="home"),
    path('test/', views.TestView.as_view(), name="test")
]