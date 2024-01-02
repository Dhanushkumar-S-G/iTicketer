from django.urls import path
from base_app.views import *
urlpatterns = [
    path('', index, name='index'),
    path('dashboard/', dashboard, name='dashboard'),
    path('logout/', logout_user, name='logout'),
    
   
]