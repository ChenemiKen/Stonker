from decimal import Decimal
from django.conf import settings
from core.models import Item, Order, OrderItem


class Cart(object):
    def __init__(self, request):
        """initialize this cart"""
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # save an empty cart in the session
            cart = self.session[settings.CART_SESSION_ID]= {}
        self.cart = cart

    def add(self, item, quantity=1, update_quantity=False):
        """ add an item to cart or update the quantity """
        item_id = str(item.id)
        if item_id not in self.cart:
            self.cart[item_id] = {'quantity':0, 'price':item.price, 'discount_price':item.discount_price}
        if update_quantity:
            self.cart[item_id]['quantity'] = quantity
        else:
            self.cart[item_id]['quantity'] += quantity
        self.save()

    def remove(self, Item):
        """ Remove an item from the cart """
        item_id = str(Item.id)
        if item_id in self.cart:
            del self.cart[item_id]
            self.save()

    def save(self):
        """ update the session cart """
        self.session[settings.CART_SESSION_ID]= self.cart
        #mark the session as modified to make sure it is saved
        self.session.modified = True

    def __iter__(self):
        """ Iterate over the items in the cart and get them from the database""" 
        item_ids = self.cart.keys()
        #get the items objects and add them to the cart
        items = Item.objects.filter(id__in=item_ids)
        for item in items:
            self.cart[str(item.id)]['item']= item

        for item in self.cart.values():
            # item['price'] = Decimal(item['price'])
            item['total_item_price'] = item['price']*item['quantity']
            if not item['discount_price'] is None:
                item['total_discount_item_price'] = item['discount_price']*item['quantity']
                item['amount_saved'] = item['total_item_price'] - item['total_discount_item_price']
                item['final_item_price'] = item['total_discount_item_price']
            else :
                item['final_item_price'] = item['total_item_price']
            yield item
       

    def __len__(self):
        """ the count of the items in the Cart """
        return sum(item['quantity'] for item in self.cart.values())


    def get_total_price(self):
        return sum(item['final_item_price'] for item in self.cart.values())
        
        
        

    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True