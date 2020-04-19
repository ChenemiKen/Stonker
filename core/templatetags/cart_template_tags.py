from django import template
from core.cart import Cart

register = template.Library()

@register.filter
def cart_item_count(request):
    cart = Cart(request)
    if hasattr(cart, 'cart'):
        return len(cart.cart)
    return 0