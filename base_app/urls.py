from django.urls import path,include
from base_app.views import *

urlpatterns = [
    path('', index, name='index'),
    path('dashboard/', dashboard, name='dashboard'),
    path('pay-success/', succ_pay, name="succ_pay"),
    path('failure/', failure, name="failure"),
    path('cancel/', cancel, name="cancel"),
    path('book_show/', pay_show, name="book_show"),
    path('logout/', logout_user, name='logout'),
    path('check_profile/<int:id>', check_profile, name='check_profile'),
    path('create_profile/', create_profile, name='create_profile'),
]