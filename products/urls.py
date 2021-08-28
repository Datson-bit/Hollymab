from django.urls import path
from .views import Home,Terms,Privacy, initiate_payment,verify_payment, search,CheckoutView,about, OrderSummaryView,remove_single_item_from_cart, contact, add_to_cart, remove_from_cart, AllProducts, View, staff, brand, AddAll

urlpatterns=[
    path('', Home, name="Home"),
    path('staff/', staff, name="staff"),
    path('about/', about, name="About"),
    path('brand/', brand),
    path('privacy/', Privacy, name="privacy"),
    path('Terms and Conditions/', Terms, name="terms"),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('contact/',contact, name="Contact" ),
    path('results/', search, name='search_results'),
    path('products/',AllProducts.as_view(), name="products"),
    path('post/', AddAll.as_view(), name="add"),
    path('add-to-cart/<int:pk>/',add_to_cart, name='add-to-cart' ),
    path('view/<int:pk>/', View.as_view(), name="view"),
    path('remove-from-cart/<int:pk>', remove_from_cart, name='remove-from-cart'),
    path('remove-item-from-cart/<int:pk>/', remove_single_item_from_cart, name='remove-single-item-from-cart'),
    path('checkout/', CheckoutView.as_view(),name="checkout"),
    path('payment/', initiate_payment, name='initiate-payment'),
    path('<str:ref>/', verify_payment, name='verify-payment')
]