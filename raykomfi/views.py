from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from .forms import SignupForm, SigninForm, NewPostForm, CustomChangePasswordForm, CustomPasswordResetForm, CommentForm, ReplyForm
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from .tokens import account_activation_token
from .models import User, Post, Comment, Reply, Message
from django.core.mail import EmailMessage
from django.contrib import messages
from django.db.utils import IntegrityError
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.contrib.sites.shortcuts import get_current_site
from django.utils.functional import SimpleLazyObject
from django.db.models import Q


from pdb import set_trace


def index(request):
    posts = Post.objects.all()
    return render(request, 'sections/home.html', context={'posts': posts})


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
                messages.success(
                    request, 'اسم المستخدم أو كلمة المرور خاطئة', extra_tags='red white-text')
                return render(request, 'user/signin.html', context={'form': form})
        else:
            return render(request, 'user/signin.html', context={'form': form})
    else:
        if request.user.is_anonymous and 'next' in request.GET:
            messages.success(
                request, 'يجب عليك تسجيل الدخول اولا', extra_tags='yellow accent-4 black-text')
        form = SigninForm(use_required_attribute=False)
        return render(request, 'user/signin.html', context={'form': form})


def user_logout(request):
    logout(request)
    messages.success(
        request, 'تم تسجيل الخروج', extra_tags='green white-text')
    return HttpResponseRedirect('/user/signin/')


def sign_up_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST, use_required_attribute=False)

        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            mail_subject = 'تفعيل حسابك على رايكم في'
            to_email = form.cleaned_data.get('email')
            from_email = 'no-reply@raykomfi.com'
            # Send data to email template and get email template.
            html_email_template = get_template("user/acc_activate_email.html").render(
                {
                    'site': SimpleLazyObject(lambda: get_current_site(request)),
                    'user': user,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': default_token_generator.make_token(user),
                }
            )
            msg = EmailMultiAlternatives(
                f"{mail_subject}", "nothing", from_email, [to_email])
            msg.attach_alternative(html_email_template, "text/html")
            msg.send()
            messages.success(
                request, 'تم انشاء الحساب, يرجى مراجعة بريدك الالكتروني, سوف تجد رسالة فيها رابط التفعيل لتفعيل حسابك', extra_tags='green white-text')

            return HttpResponseRedirect('/user/signin')

        else:
            return render(request, 'user/register.html', context={'form': form})

    else:
        form = SignupForm(use_required_attribute=False)
        return render(request, 'user/register.html', context={'form': form})


@ login_required
def post_view(request, id, slug):
    post = Post.objects.prefetch_related('comments').prefetch_related('comments__replies').get(Q(id__exact=id) & Q(
        slug__exact=slug))
    comment_form = CommentForm()
    reply_form = ReplyForm()
    return render(request, 'sections/post_view.html', context={'post': post, 'comment_form': comment_form, 'reply_form': reply_form})


@ login_required
def post_edit(request, id, slug):
    instance = get_object_or_404(Post, id=id, slug=slug)
    if request.method == 'POST':
        form = NewPostForm(request.POST or None, request.FILES or None, instance=instance,
                           use_required_attribute=False)
        if form.is_valid():
            form.save()
            instance = get_object_or_404(Post, id=id)
            return render(request, 'sections/post_view.html', context={'form': form, 'post': instance})
        else:
            return render(request, 'sections/edit_post.html', context={'form': form, 'post': instance})
    else:
        post = Post.objects.get(Q(id__exact=id) & Q(slug__exact=slug))
        form = NewPostForm(instance=instance, use_required_attribute=False)
        return render(request, 'sections/edit_post.html', context={'form': form, 'post': post})


@ login_required
def create_post(request):
    if request.method == 'POST':
        form = NewPostForm(request.POST or None, request.FILES or None,
                           use_required_attribute=False)
        if form.is_valid():
            post = form.save(commit=False)
            post.creator = request.user
            post.save()
            comment_form = CommentForm()
            reply_form = ReplyForm()
            return render(request, 'sections/post_view.html', context={'post': post, 'comment_form': comment_form, 'reply_form': reply_form})
        else:
            return render(request, 'sections/create_post.html', context={'form': form})
    else:
        form = NewPostForm(use_required_attribute=False)
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


@login_required
def add_comment(request, post_id):
    comment_form = CommentForm(request.POST or None)
    post = Post.objects.prefetch_related(
        'comments').prefetch_related('comments__replies').get(id__exact=post_id)
    if comment_form.is_valid():
        comment = Comment.objects.create(
            content=comment_form.cleaned_data['content'], user=request.user, post=post)
        messages.success(
            request, 'تم اضافة تعليقك بنجاح', extra_tags='green white-text')
        return HttpResponseRedirect(post.get_absolute_url())
    else:
        return render(request, 'sections/post_view.html', {'post': post, 'comment_form': comment_form})

    post = Post.objects.get(id__exact=post_id)
    comment = Comment.objects.create(
        user=request.user, content=data['content'], )
    post.comments.add()
    return redirect('')


@login_required
def add_reply(request, post_id, comment_id):
    reply_form = ReplyForm(request.POST or None)
    comment_form = CommentForm(request.POST or None)
    comment = Comment.objects.prefetch_related('replies').get(id=comment_id)
    post = Post.objects.prefetch_related(
        'comments').prefetch_related('comments__replies').get(id__exact=post_id)
    if reply_form.is_valid():
        reply = Reply.objects.create(
            content=reply_form.cleaned_data['content'], user=request.user, comment=comment)
        messages.success(
            request, 'تم اضافة ردك بنجاح', extra_tags='green white-text')
        return HttpResponseRedirect(post.get_absolute_url())
    else:
        return render(request, 'sections/post_view.html', {'post': post, 'comment_form': comment_form, 'reply_form': replyt_form})

    post = Post.objects.get(id__exact=post_id)
    comment = Comment.objects.create(
        user=request.user, content=data['content'], )
    post.comments.add()
    return redirect('')


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(
            request, 'تم تفعيل حسابك, يمكنك الان استخدام الموقع', extra_tags='green white-text')
        return redirect('raykomfi:user-signin')
    else:
        return render(request, 'user/activate_fail.html')
