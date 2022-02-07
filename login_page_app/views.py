from base64 import urlsafe_b64decode, urlsafe_b64encode
from email.message import EmailMessage
from lib2to3.pgen2.tokenize import generate_tokens
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from frontend_connect_1 import settings
from django.core.mail import EmailMessage, send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from . tokens import generate_token

# Create your views here.
def home(request):
    return render(request, "login_page_app/index.html")

def signup(request):

    if request.method == "POST":
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        if User.objects.filter(username=username):
            messages.error(request, "Username already exists! Use something like 🐮")
            return redirect('home')


        if User.objects.filter(email=email):
            messages.error(request, 'Email already exists, use something like 💩')
            return redirect('home')

        if len(username)>10:
            messages.error(request, "Username must be under 10 chars")

        if pass1 != pass2:
            messages.error(request, "Passwords don't match")

        if not username.isalnum():
            messages.error(request, "Username must be Alpha-numeric!")
            return redirect('home')

        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.is_active = False
        myuser.save()

        messages.success(request, "Your account has been created successfully!\nConfirmation email sent, so confirm your email to activate your account bruh 😠.")


        # Welcome Email
        subject = "Welcome to THE HOUSE OF DARCS !!"
        message = "Hello " + myuser.first_name + "!! \n" + "Welcome to THOC!!\nThank you for visiting fam\nThis is a confirmation email we're sending you bruh, so do the deed of confirming your email address\nMakes sense??\n\nThanks fam \nPeace out from the THOC guys ✌"
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)

        #Email Address
        current_site = get_current_site(request)
        email_subject = "Confirm your email @THE HOUSE OF DARCS!"
        message2 = render_to_string('email_confirmation.html', {
            'name':myuser.first_name,
            'domain':current_site.domain,
            'uid':urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token':generate_token.make_token(myuser)
        })  
        email = EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [myuser.email],
        )
        email.fail_silently = True
        email.send()

        return redirect('signin')

    return render(request, "login_page_app/signup.html")

def signin(request):

    if request.method == 'POST':
        username = request.POST['username']
        pass1 = request.POST['pass1']

        user = authenticate(username=username, password=pass1)

        if user is not None:
            login(request, user)
            fname = user.first_name
            return render(request, "login_page_app/index.html", {'fname': fname})
        else:
            messages.error(request, "Bad Credentials")
            return redirect('home')


    return render(request, "login_page_app/signin.html")

def signout(request):
    logout(request)
    messages.success(request, "Successfully logged out")
    return redirect('home')

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
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
        
