from django.shortcuts import render, redirect

from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.sites.shortcuts import get_current_site

from django.core.mail import send_mail, EmailMessage

from django.template.loader import render_to_string

from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text

from .tokens import generate_token

from login_function.settings import EMAIL_HOST_USER_ADDRESS


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
        user_email = email
        myuser.is_active = False
        
        myuser.save()
    
        messages.success(request, "Your account has been successfully created. We have sent you a confirmation email, please confirm your email in order to activate your account.")
        
        # Welcome Email
        subject = 'Welcome to GFG - Django Login!!'
        message = 'Hello' + myuser.first_name + '!! \n' + 'Welcome to GFG!! \n Thank you for visiting our website. \n We have also sent you a confirmation email, please confirm your email address in order to activate your account. \n\n Thangking You Anonymous person.\n '
        to_list = [user_email]
        send_mail(subject, message, EMAIL_HOST_USER_ADDRESS, to_list, fail_silently=False)
        
        
        # Email Address Confirmation Email
        
        current_sute = get_current_site(request)
        email_subject = 'Confirm your email @ GFG - Django Login!!'
        message2 = render_to_string('email_confirmation.html', {
            'name' : myuser.first_name,
            'domain' : current_sute.domain,
            'uid' : urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token' : generate_token.make_token(myuser),
        })
        email = EmailMessage(
            email_subject,
            message2,
            EMAIL_HOST_USER_ADDRESS,
            [myuser.email],            
        )
        email.fail_silently = False
        email.send()
        
        
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

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        myuser = None
        
    if myuser is not None and generate_token.check_token(myuser, token):
        myuser.is_active = True
        myuser.save()
        login(request, myuser)
        return redirect('home')
    else:
        return render(request, 'activation_failed.html')