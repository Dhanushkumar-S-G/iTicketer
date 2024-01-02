from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login
from django.shortcuts import redirect
from django.contrib.auth import logout
# Create your views here.
def index(request):
    return render(request,'base_app/index.html')

def dashboard(request):
    return render(request,'base_app/dashboard.html')

def callback(request):
      # Get the state saved in session      expected_state = request.session.pop('auth_state', '')
      # Make the token request      token = get_token_from_code(request.get_full_path(), expected_state)      # Get the user's profile      user = get_user(token)
      # Get user info      # user attribute like displayName,surname,mail etc. are defined by the       # institute incase you are using single-tenant. You can get these       # attribute by exploring Microsoft graph-explorer.
      username = user['displayName']
      password = user['surname']
      email = user['mail']
    #   try:
          # if use already exist          user = User.objects.get(username=username)
    #   except User.DoesNotExist:
           
          # if user does not exist then create a new user          user = User.objects.create_user(username,email,password)          user.save()
      user = authenticate(username=username,password=password)
      if user is not None:
          login(request,user)
          messages.success(request,"Success: You were successfully logged in.")
          return redirect('home')
      return redirect('home')

def logout_user(request):
    logout(request)
    return redirect("/")