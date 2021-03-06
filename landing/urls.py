from django.urls import path, include
from . import views
urlpatterns = [
    path('home/', views.HomeView.as_view(), name="home"),
    path('prices/', views.PriceListsView.as_view(), name="prices"),
    path('trademarks/', views.TrademarksView.as_view(), name="trademarks"),
    path('about/', views.AboutView.as_view(), name="about"),
    path('contacts/', views.ContactsView.as_view(), name="contacts"),
    path('cart/', views.CartView.as_view(), name="cart"),
    path('checkout/', views.CheckoutView.as_view(), name="checkout"),
    path('payment/', views.PaymentView.as_view(), name='payment'),
    path('payment-info/', views.PaymentInfoView.as_view(), name='payment-info'),
    path('', include('items.urls')),
    path('test/', views.TestView.as_view(), name="test")
]