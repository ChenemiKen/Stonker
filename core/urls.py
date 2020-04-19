from django.urls import path
from core.views import (Homeview,ItemDetailsView,AddToCart,decrease_quantity,remove_from_cart,
                        ordersummary, CheckoutView, PaymentView,)


urlpatterns = [
    path('', Homeview.as_view(), name='home'), 
    path('itemdetail/<int:pk>', ItemDetailsView.as_view(), name='item_details'), 
    path('add_to_cart/<int:pk>', AddToCart.as_view(), name='add_to_cart'),
    path('remove_from_cart/<int:pk>', remove_from_cart, name='remove_from_cart'),
    path('decrease_quantity/<int:pk>', decrease_quantity, name='decrease_quantity'),
    path('ordersummary/', ordersummary, name='ordersummary'), 
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('payment/<payment_option>/', PaymentView.as_view(), name='payment'),

]