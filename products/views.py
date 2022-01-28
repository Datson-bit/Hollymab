from django.contrib import messages
from email import message

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.utils import timezone
from django.views.generic import ListView,View, DetailView, CreateView

from . import forms
from .forms import CheckoutForm, PaymentForm, RemarkForm
from .models import Product, Item, OrderItem, Staff, Carousel, Order, BillingAddress, Payment
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings


def Home(request):
    if request.method == "POST":
        remark_form= forms.RemarkForm(request.POST, request.user)
        remark_form.get(user=request.user)
        if remark_form.is_valid():
            remark= remark_form.save()
            messages.success("Remark Posted Successfully")
            return render(request, 'index.html', {'remark': remark})
    else:
        product = Product.objects.all()
        remark_form = RemarkForm(request.POST, request.user)
        carousel= Carousel.objects.all()
        return render(request, 'index.html', {'product': product, 'carousel':carousel, 'remark':remark_form })


def initiate_payment(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        payment_form= forms.PaymentForm(request.POST)
        if payment_form.is_valid():
            order = Order.objects.get(user=request.user, ordered=False)
            payment = payment_form.save()
            return render(request, 'payment.html', {'payment': payment,'object':order, 'paystack_public_key' : settings.PAYSTACK_PUBLIC_KEY})

    else:
        order = Order.objects.get(user=request.user, ordered=False)
        payment_form = forms.PaymentForm()
    return render(request, 'initiate_payment.html', {'object':order,'payment_form':payment_form})

    return render(request, 'payment.html')



def verify_payment(request: HttpRequest, ref:str)-> HttpResponse:
    payment = get_object_or_404(Payment, ref=ref)
    verified= payment.verify_payment()
    if verified:
        messages.success(request, "verification Successful")
        return render(request, 'verify.html')
    else:
        messages.error(request, "verification failed")
    return redirect('initiate-payment')

class CheckoutView(View):
    def get(self, *args, **kwargs):
        form= CheckoutForm()
        return render(self.request, 'checkout.html', {'form':form})

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                street_address = form.cleaned_data.get('street_address')
                apartment_address = form.cleaned_data.get('apartment_address')
                country = form.cleaned_data.get('country')
                zip = form.cleaned_data.get('zip')
                # TODO: add functionality to these fields
                #same_shipping_address = form.cleaned_data['same_billing_address']
                #save_info = form.cleaned_data['save_info']

                payment_option = form.cleaned_data.get('payment_option')
                billing_address = BillingAddress(
                    user=self.request.user,
                    street_address=street_address,
                    apartment_address=apartment_address,
                    country=country,
                    zip=zip,
                )
                billing_address.save()
                order.billing_address= billing_address
                order.save()
                # TODO: add a redirect to the selected option
                return redirect("initiate-payment")
            messages.warning(self.request, "failed Checkout")
            return redirect("checkout")
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return redirect("order-summary")


def contact(request):
    if request.method == "POST":
        message_name = request.POST['message-name']
        message_email = request.POST['message-email']
        message = request.POST['message']

        send_mail(message_name, message, message_email,[settings.EMAIL_HOST_USER])
        return render(request, 'contact.html', {'message_name': message_name})

    else:
        return render(request, 'contact.html', {})


def about(request):
    return render(request, 'about.html')


def staff(request):
    employee = Staff.objects.all()
    context = {'employees':employee}
    return render(request, 'staff.html', context)


def brand(request):
    return render(request, 'brand.html', )


class AllProducts(ListView):
    model = Item
    template_name = 'products.html'


class View(DetailView):
    model = Item
    template_name = 'view.html'


class AddAll(CreateView):
    model = Item
    template_name = 'add_products.html'
    fields = '__all__'


def Terms(request):
    return render(request, 'terms.html')

def Privacy(request):
    return render(request,'Privacy.html')


class OrderSummaryView(LoginRequiredMixin, View):
   def get(self, *args, **kwargs):
       try:
           order = Order.objects.get(user=self.request.user, ordered=False)
           context={
               'object':order
           }
           return render(self.request, 'cart.html', context)

       except ObjectDoesNotExist:
           messages.error(self.request,"You do not have an active order" )
           return redirect("/")

@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, id=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user= request.user,
        ordered=False
    )
    order_qs= Order.objects.filter(user=request.user, ordered=False )
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item_id= item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This Item quantity was updated.")
            return redirect("order-summary")
        else:
            messages.info(request, "This Item was added to your cart.")
            order.items.add(order_item)
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This Item was added to your cart.")

    return redirect("view", id=slug)

@login_required
def remove_from_cart(request, pk):
    item = get_object_or_404(Item, pk=pk)
    order_qs = Order.objects.filter(


        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item_id=item.pk).exists():
            order_item= OrderItem.objects.filter(
                item=item,
                user= request.user,
                ordered=False,
            )[0]

            order.items.remove(order_item)
            messages.info(request, "This Item was removed from your cart your cart.")

        else:
            messages.info(request, "This Item was not in your cart.")
            return redirect("order-summary")
    else:
        messages.info(request, "You do not have an order.")
    return redirect("order-summary")

@login_required
def remove_single_item_from_cart(request, pk):
    item = get_object_or_404(Item, pk=pk)
    order_qs = Order.objects.filter(


        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item_id=item.pk).exists():
            order_item= OrderItem.objects.filter(
                item=item,
                user= request.user,
                ordered=False,
            )[0]

            if order_item.quantity >1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)

            messages.info(request, "This Item was updated.")
            return redirect("order-summary")
        else:
            messages.info(request, "This Item was not in your cart.")
            return redirect("view", pk=pk)
    else:
        messages.info(request, "You do not have an order.")
    return redirect("view", pk=pk)


def search(request):
    if request.method == 'GET':
        searched= request.GET.get('searched')
        items= Item.objects.all().filter(name=searched)
        return render(request, 'search_results.html', { 'items':items})
