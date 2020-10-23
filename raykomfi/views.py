from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from .forms import SignupForm, SigninForm, NewPostForm, CustomChangePasswordForm, CustomPasswordResetForm, CommentForm, ReplyForm, ProfileForm, MessageForm, RestorePasswordForm
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from .tokens import account_activation_token
from .models import User, Post, Comment, Reply, Message, Category
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
from django.urls import NoReverseMatch
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import OuterRef, Subquery, Prefetch
from .filters import PostFilter
from notifications.signals import notify
from notifications.models import Notification
from django.db.models import Count



from pdb import set_trace

def index(request):
    posts = Post.objects.all().prefetch_related('creator', 'category', 'comments')[:10]
    latest_comments = Comment.objects.prefetch_related('user', 'post', 'replies').all().order_by('-created')[:10]
    categories = Category.objects.all()
    return render(request, 'sections/home.html', context={'posts': posts, 'latest_comments': latest_comments, 'categories': categories})

def categorized_posts(request, category=False):
    posts = Post.objects.prefetch_related('creator', 'category', 'comments').filter(category__name__exact=category)[:10]
    categories = Category.objects.all()
    latest_comments = Comment.objects.all().prefetch_related('user', 'post', 'replies').order_by('-created')[:7]
    return render(request, 'sections/home.html', context={'posts': posts, 'latest_comments': latest_comments, 'categories': categories, 'is_categorized': True, 'category': category})

def most_discussed_posts(request):
    posts = Post.objects.prefetch_related('creator', 'category', 'comments').annotate(count=Count('comments')).order_by('-count')
    categories = Category.objects.all()
    latest_comments = Comment.objects.all().prefetch_related('user', 'post', 'replies').order_by('-created')[:7]
    return render(request, 'sections/home.html', context={'posts': posts, 'latest_comments': latest_comments, 'categories': categories, 'hide_load_more': True})


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
            stay_logged_in = request.POST.get('stay_logged_in', 'off')
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    if stay_logged_in == 'on':
                        user.stay_logged_in = True
                        user.save()
                    else:
                        user.stay_logged_in = False
                        user.save()
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
                request, 'يجب عليك تسجيل الدخول أولا', extra_tags='pale-yellow w3-border')
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

@login_required
def delete_user(request, id):
    user = User.objects.get(id=id)
    question = request.GET['question']
    if question != 'true':
        user.is_active = False
        user.save()
        messages.success(
                request, 'تم حذف حسابك, لكن إستفساراتك, تعليقاتك و ردودك ستبقى لكن بدون إسمك الشخصي, في حال قررت إسترجاع حسابك يرجى التواصل مع الدعم support@raykomfi.com', extra_tags='pale-green w3-border')
        return redirect('raykomfi:user-signin')
    else:
        return render(request, 'sections/are_you_sure.html')

def post_view(request, id, slug):
    subquery = Subquery(Comment.objects.filter(post__id=OuterRef('post__id')).values_list('id', flat=True)[:5])
    post = Post.objects.select_related('creator', 'category').filter(Q(id__exact=id) & Q(
        slug__exact=slug)).prefetch_related('creator', Prefetch('comments', queryset=Comment.objects.filter(id__in=subquery).prefetch_related('user', 'replies__user', 'post', 'post__creator', 'voted_like', 'voted_dislike'))).first()
    rand_ids = Post.objects.select_related('creator', 'category').filter(category=post.category).values_list('id', flat=True)
    rand_ids = list(rand_ids)
    rand_ids = sample(rand_ids, 7)
    related_posts = Post.objects.select_related('creator', 'category').filter(id__in=rand_ids)
    comment_form = CommentForm()
    reply_form = ReplyForm()
    if request.GET.get('read'):
        full_path = request.get_full_path()
        notis = Notification.objects.filter(description__icontains=full_path)
        if notis: 
            notis.first().delete()
    return render(request, 'sections/post_view.html', context={'post': post, 'comment_form': comment_form, 'reply_form': reply_form, 'related_posts': related_posts})


@ login_required
def my_posts_view(request, user_id):
    posts = Post.objects.prefetch_related('creator', 'category').filter(creator__id=user_id)
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
            set_trace()
            return redirect(post.get_absolute_url())
        else:
            return render(request, 'sections/create_post.html', context={'form': form})
    else:
        form = NewPostForm(use_required_attribute=False)
        return render(request, 'sections/create_post.html', context={'form': form})

@login_required
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

def restore_password_view(request):
    if request.method == 'POST':
        try:
            user = User.objects.get(id=request.POST['id'], email=request.POST['email'], secret_code=request.POST['secret_code'])
        except:
            return redirect('raykomfi:user-signin')
        if user:
            form = RestorePasswordForm(
                request.POST, use_required_attribute=False)
            if form.is_valid() and user:
                password = form.cleaned_data['password2']
                user.set_password(password)
                user.save()
                messages.success(
                    request, 'تم إعادة تعيين كلمة المرور بنجاح', extra_tags='pale-green w3-border')
                return redirect('raykomfi:user-signin')
            else:
                return render(request, 'user/restore_password.html', {
                    'form': form,
                    'user': user
                })
        else:
            return redirect('raykomfi:user-signin')
def forgot_password_view(request):
    if request.method == 'POST':
        form = CustomPasswordResetForm(request.POST ,use_required_attribute=False)
        if form.is_valid():
            user = get_object_or_404(User, email=form.cleaned_data['email'])
            current_site = get_current_site(request)
            mail_subject = 'رابط تغيير كلمة المرور'
            to_email = form.cleaned_data.get('email')
            from_email = 'no-reply@raykomfi.com'
            # Send data to email template and get email template.
            html_email_template = get_template("user/restore_password_email_view.html").render(
                {
                    'site': SimpleLazyObject(lambda: get_current_site(request)),
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': default_token_generator.make_token(user),
                    'id': user.id
                }
            )
            msg = EmailMultiAlternatives(
                f"{mail_subject}", "nothing", from_email, [to_email])
            msg.attach_alternative(html_email_template, "text/html")
            msg.send()
            messages.success(
                request, 'تم إرسال رابط إعادة تعيين كلمة المرور إلى بريدك الإلكتروني', extra_tags='pale-green w3-border')

            return HttpResponseRedirect('/user/signin')
        else:
            return render(request, 'user/forgot_password.html', context={'form': form})
    else:
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
            notify.send(request.user, recipient=receiver ,action_object=message, description=message.get_noti_url(), target=message, verb='message')
            return redirect(receiver.get_absolute_url())
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

@login_required
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

    return redirect(comment.post.get_absolute_url())

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
        return HttpResponseRedirect(post.get_absolute_url() + f'#to-{reply.id}')
    else:
        return render(request, 'sections/post_view.html', {'post': post, 'comment_form': comment_form, 'reply_form': reply_form})

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        if user.email_active == True:
            messages.success(
            request, 'حسابك مفعل من قبل', extra_tags='pale-green w3-border')
        return redirect('raykomfi:user-signin')
        user.email_active = True
        user.save()
        logout(request)
        messages.success(
            request, 'تم تفعيل حسابك, يمكنك الان استخدام الموقع', extra_tags='pale-green w3-border')
        return redirect('raykomfi:user-signin')
    else:
        return render(request, 'user/activate_fail.html')

def restore_password(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        form = RestorePasswordForm(use_required_attribute=False)
        return render(request, 'user/restore_password.html', {'form': form, 'user': user})
    else:
        return render(request, 'user/activate_fail.html', {'user': user})

def send_link(request):
    if request.method == 'POST':
        current_site = get_current_site(request)
        email = request.POST.get('email')
        if '@' not in email:
            messages.success(
                request, 'أدخل بريد إلكتروني صحيح, أعد المحاولة مرة أخرى', extra_tags='pale-red w3-border')
            return redirect('raykomfi:sign-in')
        to_email = email
        user = get_object_or_404(User, email=to_email)
        mail_subject = 'تفعيل حسابك على رايكم في'
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
            request, 'تم إرسال رابط التفعيل الى بريدك الإلكتروني', extra_tags='pale-green w3-border')

        return HttpResponseRedirect('/user/signin')

    else:
        return render(request, 'user/activate_account.html')