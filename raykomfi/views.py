from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import SignupForm, SigninForm, NewPostForm, CustomChangePasswordForm, CustomPasswordResetForm
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
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect


from pdb import set_trace


# Create your views here.


def index(request):
    return render(request, 'sections/home.html')


@login_required
def profile_view(request, id):
    return render(request, 'user/profile.html')


def sign_in_view(request):
    if request.method == 'POST':
        form = SigninForm(request.POST, use_required_attribute=False)
        if form.is_valid():
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect(reverse('raykomfi:raykomfi-home'))
            else:
                messages.warning(request, 'حساب غير موجود')
                return render(request, 'user/signin.html', context={'form': form})
        else:
            return render(request, 'user/signin.html', context={'form': form})
    else:
        if request.user.is_anonymous and request.GET['next']:
            messages.warning(request, 'يجب عليك تسجيل الدخول اولا')
        form = SigninForm(use_required_attribute=False)
        return render(request, 'user/signin.html', context={'form': form})


def user_logout(request):
    logout(request)
    messages.success(request, 'تم تسجيل الخروج')
    return HttpResponseRedirect('/user/signin/')


def sign_up_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST, use_required_attribute=False)

        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            # user.save()
            current_site = get_current_site(request)
            mail_subject = 'تفعيل حسابك على رايكم في'
            message = render_to_string('user/acc_activate_email.html', {
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
        form = SignupForm(use_required_attribute=False)
        return render(request, 'user/register.html', context={'form': form})


@ login_required
def post_view(request, id):
    return render(request, 'sections/post_view.html')


@ login_required
def create_post(request):
    if request.method == 'POST':
        pass
    else:
        form = NewPostForm()
    return render(request, 'sections/create_post.html', context={'form': form})


def change_password_view(request):
    if request.method == 'POST':
        form = CustomChangePasswordForm(
            request.user, request.POST, use_required_attribute=False)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(
                request, 'Your password was successfully updated!')
            return redirect('raykomfi:raykomfi-home')
        else:
            return render(request, 'user/change_password.html', {
                'form': form
            })
    else:
        form = CustomChangePasswordForm(
            request.user, use_required_attribute=False)
        return render(request, 'user/change_password.html', {
            'form': form
        })


def forgot_password_view(request):
    if request.method == 'POST':
        form = CustomPasswordResetForm(
            request.POST, use_required_attribute=False)
        if form.is_valid():
            pass
        else:
            return render(request, 'user/forgot_password.html', context={'form': form})
    else:
        form = CustomPasswordResetForm(use_required_attribute=False)
        return render(request, 'user/forgot_password.html', context={'form': form})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        # return redirect('home')
        return render(request, 'user/change_password.html', context={'condition': 'success', 'message': 'يرجى ادخال كلمة '})
    else:
        return render(request, 'user/activate_success_fail.html', context={'condition': 'fail', 'message': 'رابط التفعيل منتهي الصلاحية حاول مرة اخرى'})
