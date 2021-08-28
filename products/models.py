from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from ckeditor.fields import RichTextField
from django.urls import reverse
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
import secrets

from paystackapi.paystack import Paystack

from products.paystack import PayStack

CATEGORY_CHOICES=[
    ("T", "Tecno"),
    ('I', 'Itel'),
    ('In', 'Infinix'),
    ('Sm', 'Samsung'),
    ('Ip', 'Iphone'),
    ('H', 'Huwaei'),
    ('F', 'Fero'),
    ('O', 'Oppo')
]

LABEL_CHOICES = (
    ('P', 'primary'),
    ('D', 'danger'),
    ('S', 'Secondary'),
    ('W', 'warning'),
    ('I', 'info'),
    ('D', 'dark')
)

class Carousel(models.Model):
    img= models.CharField(max_length=2083, default="")
    name= models.CharField(max_length=200, default="p")
    alt= models.CharField(max_length=250, default="sl")
    des= models.CharField(max_length=255, default="")



class Product(models.Model):
    img_url = models.CharField(max_length=2083, default="")
    price = models.FloatField()
    name= models.CharField(max_length=50)

    def get_absolute_url(self):
        return reverse('view1', args=(str(self.id)))


class Item(models.Model):
    img_url = models.CharField(max_length=2083, default="")
    price = models.FloatField()
    discount= models.FloatField(max_length=100, blank=True, null=True)
    body = RichTextField(blank=True,  null=True)
    name = models.CharField(max_length=50)
    category= models.CharField(choices=CATEGORY_CHOICES, max_length=2, default="")
    label= models.CharField(choices=LABEL_CHOICES, max_length=1, default="")



    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('core:view', args=(str(self.id)))

    def get_add_to_cart_url(self):
        return reverse('add-to-cart', args=(str(self.id)))


    def get_remove_from_cart_url(self):
        return reverse('remove-from-cart', args=(str(self.id)))


class Staff(models.Model):
    name= models.CharField(max_length=100)
    position= models.CharField(max_length=50)
    img= models.ImageField(default="", upload_to='images/')


class OrderItem(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity= models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.item.name}"

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_discount_item_price(self):
        return self.quantity * self.item.discount

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.item.discount:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()

class Order(models.Model):
    user= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    start_date= models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    billing_address= models.ForeignKey('BillingAddress', on_delete=models.SET_NULL, blank=True,null=True)
    payment= models.ForeignKey('Payment', on_delete=models.SET_NULL, blank=True,null=True)

    def __str__(self):
        return self.user.username

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        return total


class BillingAddress(models.Model):
    user= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    street_address=models.CharField(max_length=100)
    apartment_address= models.CharField(max_length=100)
    country= CountryField(multiple=False, default="")
    zip = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username


class Payment(models.Model):
    amount= models.PositiveIntegerField()
    ref= models.CharField(max_length=200)
    email= models.EmailField()
    verified = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-date_created',)

    def __str__(self) -> str:
        return f"Payment: {self.amount}"

    def save(self, *args, **kwargs) -> None:
        while not self.ref:
            ref = secrets.token_urlsafe(50)
            object_with_similar_ref = Payment.objects.filter(ref=ref)
            if not object_with_similar_ref:
                self.ref = ref
        super().save(*args, **kwargs)

    def amount_value(self) -> int:
        return self.amount *100+50000

    def verify_payment(self):
        paystack = PayStack()
        status, result = paystack.verify_payment(self.ref, self.amount)
        if status:
            if result['amount']/100+50000 ==self.amount:
                self.verified=True
            self.save()
        if self.verified:
            return True
        return False


class Remark(models.Model):
    user= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    body=  models.TextField()
    date = models.DateTimeField(auto_now_add=True)