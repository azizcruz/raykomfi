from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from .forms import SignupForm, SigninForm, NewPostForm, CustomChangePasswordForm, CustomPasswordResetForm, CommentForm, ReplyForm, ProfileForm, MessageForm
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
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.contrib.sites.shortcuts import get_current_site
from django.utils.functional import SimpleLazyObject
from django.db.models import Q
from random import sample

from pdb import set_trace


def index(request):
    posts = Post.objects.all()
    latest_comments = Comment.objects.all().order_by('-created')
    return render(request, 'sections/home.html', context={'posts': posts, 'latest_comments': latest_comments})


@login_required
def profile_view(request, id):
    if request.method == 'POST':
        form = ProfileForm(request.POST or None,
                           instance=request.user, use_required_attribute=False)
        if form.is_valid():
            request.user.username = form.cleaned_data['username']
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.country = form.cleaned_data['country']
            request.user.bio = form.cleaned_data['bio']
            request.user.email = form.cleaned_data['email']
            request.user.save()
            messages.success(
                request, 'تم الحفظ بنجاح', extra_tags='pale-green w3-border')
            return render(request, 'user/profile.html', context={'form': form})
        else:
            return render(request, 'user/profile.html', context={'form': form})
    else:
        if request.user.id != id:
            profile = User.objects.prefetch_related('posts').get(id=id)
            return render(request, 'user/profile.html', {'profile': profile})
        else:
            form = ProfileForm(instance=request.user,
                               use_required_attribute=False)
            return render(request, 'user/profile.html', {'form': form})


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
                    request, 'اسم المستخدم أو كلمة المرور خاطئة', extra_tags='pale-red w3-border')
                return render(request, 'user/signin.html', context={'form': form})
        else:
            return render(request, 'user/signin.html', context={'form': form})
    else:
        if request.user.is_anonymous and 'next' in request.GET:
            messages.success(
                request, 'يجب عليك تسجيل الدخول اولا', extra_tags='pale-yellow w3-border')
        if request.user.is_authenticated:
            messages.success(
                request, 'أنت مسجل الدخول بالفعل', extra_tags='pale-green w3-border')
            return redirect('/')
        form = SigninForm(use_required_attribute=False)
        return render(request, 'user/signin.html', context={'form': form})


def user_logout(request):
    logout(request)
    messages.success(
        request, 'تم تسجيل الخروج', extra_tags='pale-green w3-border')
    return HttpResponseRedirect('/user/signin/')


def sign_up_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST, use_required_attribute=False)

        if form.is_valid():
            user = form.save(commit=False)
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
                request, 'تم انشاء الحساب, يرجى مراجعة بريدك الالكتروني, سوف تجد رسالة فيها رابط التفعيل لتفعيل حسابك', extra_tags='pale-green w3-border')

            return HttpResponseRedirect('/user/signin')

        else:
            return render(request, 'user/register.html', context={'form': form})

    else:
        form = SignupForm(use_required_attribute=False)
        return render(request, 'user/register.html', context={'form': form})


@ login_required
def post_view(request, id, slug):
    post = Post.objects.prefetch_related('comments').prefetch_related('comments__replies').prefetch_related('comments__voted_like').prefetch_related('comments__voted_dislike').get(Q(id__exact=id) & Q(
        slug__exact=slug))
    rand_ids = Post.objects.filter(category=post.category).values_list('id', flat=True)
    rand_ids = list(rand_ids)
    rand_ids = sample(rand_ids, 5)
    related_posts = Post.objects.filter(id__in=rand_ids)
    comment_form = CommentForm()
    reply_form = ReplyForm()
    return render(request, 'sections/post_view.html', context={'post': post, 'comment_form': comment_form, 'reply_form': reply_form, 'related_posts': related_posts})


@ login_required
def my_posts_view(request, user_id):
    posts = Post.objects.prefetch_related('comments').prefetch_related('comments__replies').filter(creator__id=user_id)
    return render(request, 'sections/user_posts.html', context={'posts': posts})


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
                request, 'تم تغيير كلمة المرور بنجاح', extra_tags='pale-green w3-border')
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
    form = CustomPasswordResetForm(use_required_attribute=False)
    return render(request, 'user/forgot_password.html', context={'form': form})

@ login_required
def messages_view(request, user_id, message_id=0):
    if request.method == 'POST':
        message = get_object_or_404(Message, id=message_id)
        message.is_read = True
        message.save()
        user_messages = Message.objects.filter(receiver__exact=user_id)
        return render(request, 'sections/messages.html', {'user_messages': user_messages, 'fetched_message': message})
    else:
        user_messages = Message.objects.filter(receiver__exact=user_id)
        return render(request, 'sections/messages.html', {'user_messages': user_messages})
        
@ login_required
def new_message_view(request, code):
    receiver = get_object_or_404(User, uuid=code)
    if request.method == 'POST':
        form = MessageForm(
            request.POST, use_required_attribute=False)
        if form.is_valid():
            message = Message.objects.create(user=request.user, receiver=receiver, title=form.cleaned_data['title'], content=form.cleaned_data['content'])
            messages.success(
            request, f'تم إرسال الرسالة الى {receiver.username} بنجاح', extra_tags='pale-green w3-border')
            return render(request, 'sections/home.html')
        else:
            return render(request, 'sections/new_message.html', context={'form': form, 'receiver': receiver})
    else:
        form = MessageForm(use_required_attribute=False)
        return render(request, 'sections/new_message.html', context={'form': form, 'receiver': receiver})
    


@login_required
def add_comment(request, post_id):
    comment_form = CommentForm(request.POST or None)
    post = Post.objects.prefetch_related(
        'comments').prefetch_related('comments__replies').get(id__exact=post_id)
    if comment_form.is_valid():
        comment = Comment.objects.create(
            content=comment_form.cleaned_data['content'], user=request.user, post=post)
        messages.success(
            request, 'تم اضافة تعليقك بنجاح', extra_tags='pale-green w3-border')
        return HttpResponseRedirect(post.get_absolute_url())
    else:
        return render(request, 'sections/post_view.html', {'post': post, 'comment_form': comment_form})

def comment_vote(request, comment_id):
    comment = Comment.objects.prefetch_related('voted_like').prefetch_related('voted_dislike').prefetch_related('post').get(id=comment_id)
    vote_type = request.POST.get('vote')
    comment_location = request.POST.get('comment-location')

    if vote_type == 'like':
        if request.user not in comment.voted_like.all() and request.user in comment.voted_dislike.all():
            comment.voted_dislike.remove(request.user)
            comment.voted_like.add(request.user)
        else:
            comment.voted_like.add(request.user)
    
    if vote_type == 'dislike':
        if request.user not in comment.voted_dislike.all() and request.user in comment.voted_like.all():
            comment.voted_dislike.add(request.user)
            comment.voted_like.remove(request.user)
        else:
            comment.voted_dislike.add(request.user)

    comment.votes = comment.voted_like.all().count() - comment.voted_dislike.all().count()
    comment.save()

    return redirect(comment.post.get_absolute_url() + f'#location-{comment_location}')

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
            request, 'تم اضافة ردك بنجاح', extra_tags='pale-green w3-border')
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
        user.email_active = True
        user.save()
        logout(request)
        messages.success(
            request, 'تم تفعيل حسابك, يمكنك الان استخدام الموقع', extra_tags='pale-green w3-border')
        return redirect('raykomfi:user-signin')
    else:
        return render(request, 'user/activate_fail.html')
