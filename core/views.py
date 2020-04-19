from django.shortcuts import render, get_object_or_404,redirect
from django.conf import settings
from django.views.generic import ListView,DetailView,View
from core.models import Item, Order, OrderItem, BillingAddress,Payment
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django. views.decorators.http import require_POST
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from urllib.parse import urlparse
from django.urls import resolve
from core.cart import Cart
from core.forms import CartAddForm,CheckoutForm

import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

class Homeview(ListView):
    model = Item
    context_object_name = 'Items'
    template_name = 'home.html'
    paginate_by = 12



class ItemDetailsView(DetailView):
    model = Item
    context_object_name = 'item_details'
    template_name = 'product-page.html'



class AddToCart(View):
    def get(self, *args, **kwargs):
        cart = Cart(self.request)
        item = get_object_or_404(Item, id=kwargs['pk'])
        cart.add(item=item)
        return redirect("ordersummary")
        
    def post(self, *args, **kwargs):
        cart = Cart(self.request)
        item = get_object_or_404(Item, id=kwargs['pk'])
        form = CartAddForm(self.request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            cart.add(item=item, quantity=cd['quantity'], update_quantity=cd['update'])
        return redirect("ordersummary")
 


class CheckoutView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        form = CheckoutForm()
        context = {
            'form': form
        }
        return render(self.request, 'checkout.html', context)

    def post(self, *args, **kwargs):
        cart = Cart(self.request)
        order, created = Order.objects.get_or_create(user=self.request.user,ordered=False)
        item_ids = cart.cart.keys()
        items = Item.objects.filter(id__in=item_ids)
        for item in items:
            quantity = cart.cart[str(item.id)]['quantity']
            order_item, created = OrderItem.objects.get_or_create(
                item=item,
                user=self.request.user,
                ordered=False,
                quantity=quantity
            )
            order.items.add(order_item)

        form = CheckoutForm(self.request.POST or None)
        
        if form.is_valid():
            street_address = form.cleaned_data.get('street_address')
            apartment_address = form.cleaned_data.get('apartment_address')
            country = form.cleaned_data.get('country')
            zip = form.cleaned_data.get('zip')
            # TODO add funtionality for these fields
            # same_shipping_address = form.cleaned_data.get('same_shipping_address')
            # save_info form.cleaned_data.get('save_info')
            payment_option = form.cleaned_data.get('payment_option')
            billing_address = BillingAddress(
                user = self.request.user,
                street_address = street_address,
                apartment_address = apartment_address,
                country = country,
                zip = zip  
            )
            billing_address.save()
            order.billing_address = billing_address
            order.save()
            
            print(payment_option)
            if payment_option == 'stripe':
                return redirect('payment', payment_option ='stripe')
            elif payment_option == 'paypal':
                return redirect('payment', payment_option ='paypal')
            else:
                messages.warning(self.request, 'Invalid payment option selected')
                return redirect('checkout')



class PaymentView(View):
    def get(self,*args, **kwargs):
        #order
        order = Order.objects.get(user=self.request.user,ordered=False)
        context = {
            'order' : order
        }
        return render(self.request, 'payment.html', context)
    
    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user,ordered=False)
        token = self.request.POST.get('stripeToken')
        amount = int(order.get_total() * 100)
        
                    # customer.sources.create(source=token)
                    # userprofile.stripe_customer_id = customer['id']
                    # userprofile.one_click_purchasing = True
                    # userprofile.save()


        try:
            # if use_default or save:
            #     # charge the customer because we cannot charge the token more than once
            #     charge = stripe.Charge.create(
            #         amount=amount,  # cents
            #         currency="usd",
            #         customer=userprofile.stripe_customer_id
            #     )
            # else:
                # charge once off on the token
            charge = stripe.Charge.create(
                amount=amount,  # cents
                currency="usd",
                source=token
            )

            # create the payment
            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_total()
            payment.save()

            # assign the payment to the order
            # order_items = order.items.all()
            # order_items.update(ordered=True)
            # for item in order_items:
            #     item.save()

            order.ordered = True
            order.payment = payment
            # order.ref_code = create_ref_code()
            order.save()

            messages.success(self.request, "Your order was successful!")
            return redirect("/")

        except stripe.error.CardError as e:
            body = e.json_body
            err = body.get('error', {})
            messages.warning(self.request, f"{err.get('message')}")
            return redirect("/")

        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            messages.warning(self.request, "Rate limit error")
            return redirect("/")

        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            print(e)
            messages.warning(self.request, "Invalid parameters")
            return redirect("/")

        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            messages.warning(self.request, "Not authenticated")
            return redirect("/")

        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            messages.warning(self.request, "Network error")
            return redirect("/")

        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            messages.warning(
                self.request, "Something went wrong. You were not charged. Please try again.")
            return redirect("/")

        except Exception as e:
            # send an email to ourselves
            messages.warning(
                self.request, "A serious error occurred. We have been notifed.")
            return redirect("/")

        messages.warning(self.request, "Invalid data received")
        return redirect("/payment/stripe/")
            
    



def decrease_quantity(request, pk):
    cart = Cart(request)
    item = get_object_or_404(Item, id=pk)
    item_id = str(item.id)
    print(cart.__dict__)
    if cart.cart[item_id]['quantity'] > 1:
        cart.add(item=item, quantity=-1)
    else:
        cart.remove(item)
    return redirect("ordersummary")



def remove_from_cart(request, pk):
    cart = Cart(request)
    item = get_object_or_404(Item, id=pk)
    cart.remove(item)
    return redirect("ordersummary")



def ordersummary(request):
    cart = Cart(request)
    total_cart_price = sum(item['final_item_price'] for item in cart)
    context= {'cart':cart, 'total_cart_price':total_cart_price}
    return render (request, 'ordersummary.html', context)



