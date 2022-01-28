from django.urls import path
from .views import UserRegisterView, dashboard

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name= "register"),
    # path('edit/', UpdateView.as_view(), name= 'edit'),
    path('dashboard/', dashboard, name='dashboard')
]