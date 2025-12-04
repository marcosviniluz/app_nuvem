from django.urls import path
from . import views

# Definimos o namespace para usar no HTML como: {% url 'contas:login' %}
app_name = 'contas'

urlpatterns = [
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_user, name='logout'),
]