from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import SignupForm, SigninForm
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.contrib import messages
from django.db.utils import IntegrityError
from django.contrib.auth.decorators import login_required
from django.urls import reverse


from pdb import set_trace


# Create your views here.


def index(request):
    return render(request, 'sections/home.html')


def profile_view(request, id):
    return render(request, 'user/profile.html')


def sign_in_view(request):
    if request.method == 'POST':
        form = SigninForm(request.POST)
        if form.is_valid():
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect(reverse('raykomfi:raykomfi-home'))
            else:
                render(request, 'user/signin.html', context={'form': form})
        else:
            return render(request, 'user/signin.html', context={'form': form})
    else:
        form = SigninForm()
        return render(request, 'user/signin.html', context={'form': form})


def sign_up_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            mail_subject = 'تفعيل حسابك على رايكم في'
            message = render_to_string('acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            email.send()
            messages.success(
                request, 'تم انشاء الحساب, يرجى مراجعة ايميليك لتفعيل الحساب')
            return render(request, 'user/signin.com')

        else:
            return render(request, 'user/register.html', context={'form': form})

    else:
        form = SignupForm()
        return render(request, 'user/register.html', context={'form': form})


def post_view(request, id):
    return render(request, 'sections/post_view.html')


def create_post(request):
    return render(request, 'sections/create_post.html')


def change_password_view(request):
    return render(request, 'user/change_password.html')


def forgot_password_view(request):
    return render(request, 'user/_password.html')
