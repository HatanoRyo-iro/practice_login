from django.shortcuts import render, redirect

from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

from django.core.mail import send_mail
from login_function.info import EMAIL_HOST_USER_ADDRESS


# Create your views here.

def home(request):
    return render(request, 'authentication/index.html')


def signup(request):
    
    if request.method == 'POST':
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']
        
        if User.objects.filter(username=username):
            messages.error(request, "Username already exists! Please try some other username.")
            return redirect('home')
        
        if User.objects.filter(email=email):
            messages.error(request, "Email already registered!")
            return redirect('home')
        
        if len(username) > 10:
            messages.error(request, "Username must be under 10 characters!")
            
        
        if pass1 != pass2:
            messages.error(request, "Passwords don't match!")
        
        
        if not username.isalnum():
            messages.error(request, "Username must be Alphanumaric!")
            return redirect('home')
        
        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.email = email
        
        myuser.save()
    
        messages.success(request, "Your account has been successfully created. We have sent you a confirmation email, please confirm your email in order to activate your account.")
        
        # Welcome Email
        subject = 'Welcome to GFG - Django Login!!'
        message = 'Hello' + myuser.first_name + '!! \n' + 'Welcome to GFG!! \n Thank you for visiting our website. \n We have also sent you a confirmation email, please confirm your email address in order to activate your account. \n\n Thangking You Anonymous person.\n '
        
        
        to_list = [email]
        send_mail(subject, message, EMAIL_HOST_USER_ADDRESS, to_list, fail_silently=False)
        
        return redirect('signin')
    
    return render(request, 'authentication/signup.html')


def signin(request):
    
    if request.method == 'POST':
        username = request.POST['username']
        pass1 = request.POST['pass1']
        
        user = authenticate(username=username, password=pass1)
        
        if user is not None:
            login(request, user)
            params = {
                'fname' : user.first_name,
            }
            print(user.username)
            return render(request, "authentication/index.html", params)
        
        else:
            messages.error(request, "Bad Credentials!")
            return redirect('home')
    
    return render(request, 'authentication/signin.html')

def signout(request):
    logout(request)
    messages.success(request, "Logged Out Successfully!")
    return redirect('home')