import email

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.forms import  UserCreationForm
from django.template.loader import render_to_string

from hollymab import settings
from .forms import UserRegister
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.urls import reverse_lazy
from django.views import generic

class UserRegisterView(generic.CreateView):
    form_class = UserRegister
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')

    def post(self, request, *args, **kwargs):
        form= UserRegister(self.request.POST)
        if form.is_valid():
            message_name ="HOLLYMAB GLOBAL ENTERPRISE"
            context={
                'user' :self.request.POST.user
            }
            message=render_to_string('email/welcome.html', context)
            message_email = request.POST['email']
            send_mail(message_name, message,settings.EMAIL_HOST_USER, [message_email])
            return redirect('login')
        return redirect('register')

#
# class UpdateView(generic.UpdateView):
#     form = UserRegister
#     fields = ['username', 'email']
#     template_name = 'edit.html'
#     success_url = reverse_lazy('dashboard')


@login_required
def dashboard(request):
    return render(request, 'dashboard.html')