from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from .forms import SignupForm, SigninForm, NewPostForm, CustomChangePasswordForm, CustomPasswordResetForm, CommentForm, ReplyForm, ProfileForm, MessageForm, RestorePasswordForm, ForgotNoRegistrationCodeForm, ChangeEmailForm, NewPostWithNoRegistrationForm, SignupWithNoRegistrationForm
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from .tokens import account_activation_token
from .models import User, Post, Comment, Reply, Message, Category, NoRegistrationCode
from django.core.mail import EmailMessage
from django.contrib import messages
from django.db.utils import IntegrityError
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_GET
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
from ratelimit.decorators import ratelimit
from hitcount.utils import get_hitcount_model
from hitcount.views import HitCountMixin
from django.db.models import F
import secrets
from django.utils import timezone
from background_task import background
from .background_tasks import send_email, send_notify
from ratelimit.decorators import ratelimit
from django.http import JsonResponse
from rest_framework import status
from random import randint
import os
from django.db.models import Max





from pdb import set_trace

@ratelimit(key='ip', rate='50/m', block=True)
def index(request):
    posts = Post.objects.prefetch_related('creator', 'category', 'comments').filter(isActive=True)[:8]
    count = posts.count()
    latest_comments = Comment.objects.prefetch_related('user', 'post', 'replies').filter(post__isActive=True).order_by('-created')[:10]
    categories = Category.objects.all()
    if request.user.is_staff:
        posts = Post.objects.prefetch_related('creator', 'category', 'comments').all()
    return render(request, 'sections/home.html', context={'posts': posts, 'latest_comments': latest_comments, 'categories': categories, 'view_title': f'منصة رايكم في | إستفسر رأي الناس عن أي شي ', 'count': count})

@ratelimit(key='ip', rate='50/m', block=True)
def posts_with_latests_comment_order(request):
    posts = Post.objects.prefetch_related('creator', 'category', 'comments').filter(isActive=True).annotate(max_activity=Max('comments__created')).order_by('-max_activity')[:8]
    count = posts.count()
    latest_comments = Comment.objects.prefetch_related('user', 'post', 'replies').filter(post__isActive=True).order_by('-created')[:10]
    categories = Category.objects.all()
    return render(request, 'sections/home.html', context={'posts': posts, 'latest_comments': latest_comments, 'categories': categories, 'view_title': f'منصة رايكم في | إستفسر رأي الناس عن أي شي ', 'count': count})


def latest_posts(request):
    posts = Post.objects.prefetch_related('creator', 'category', 'comments').filter(isActive=True).order_by('-created')[:8]
    count = posts.count()
    latest_comments = Comment.objects.prefetch_related('user', 'post', 'replies').filter(post__isActive=True).order_by('-created')[:10]
    categories = Category.objects.all()
    return render(request, 'sections/home.html', context={'posts': posts, 'latest_comments': latest_comments, 'categories': categories, 'view_title': 'منصة رايكم في | أحدث الإستفسارات', 'count': count})

@ratelimit(key='ip', rate='50/m', block=True)
def categorized_posts(request, category=False):
    posts = Post.objects.prefetch_related('creator', 'category', 'comments').filter(category__name__exact=category, isActive=True).annotate(max_activity=Max('comments__created')).order_by('-max_activity')
    count_categoized = posts.count()
    categories = Category.objects.all()
    latest_comments = Comment.objects.prefetch_related('user', 'post', 'replies').filter(post__isActive=True).order_by('-created')[:10]
    return render(request, 'sections/home.html', context={'posts': posts, 'latest_comments': latest_comments, 'categories': categories, 'is_categorized': True, 'hide_load_more': True, 'category': category, 'view_title': f'رايكم في | { category }', 'url_name': 'categorized_view', 'count_categorized': count_categoized})


@ratelimit(key='ip', rate='50/m', block=True)
def most_discussed_posts(request):
    posts = Post.objects.prefetch_related('creator', 'category', 'comments').filter(isActive=True).annotate(count=Count('comments')).order_by('-count')
    count = posts.count()
    categories = Category.objects.all()
    latest_comments = Comment.objects.prefetch_related('user', 'post', 'replies').filter(post__isActive=True).order_by('-created')[:10]
    return render(request, 'sections/home.html', context={'posts': posts, 'latest_comments': latest_comments, 'categories': categories, 'hide_load_more': True, 'view_title': 'منصة رايكم في | الأكثر مناقشة', 'url_name': 'most_discussed_view', 'count': count})


@ratelimit(key='ip', rate='50/m', block=True)
def most_searched_posts(request):
    posts = Post.objects.prefetch_related('creator', 'category', 'comments').filter(isActive=True).order_by("-hit_count_generic__hits")
    count = posts.count()
    categories = Category.objects.all()
    latest_comments = Comment.objects.prefetch_related('user', 'post', 'replies').filter(post__isActive=True).order_by('-created')[:8]
    return render(request, 'sections/home.html', context={'posts': posts, 'latest_comments': latest_comments, 'categories': categories, 'hide_load_more': True, 'view_title': 'منصة رايكم في | الأكثر بحثا', 'url_name': 'most_searched_view', 'count': count})

@login_required
@ratelimit(key='ip', rate='10/m', block=True)
def profile_view(request, id):
    try:
        if request.method == 'POST':
            form = ProfileForm(request.POST or None,
                            instance=request.user, use_required_attribute=False)
            if form.is_valid():
                request.user.username = form.cleaned_data['username']
                request.user.first_name = form.cleaned_data['first_name']
                request.user.last_name = form.cleaned_data['last_name']
                request.user.bio = form.cleaned_data['bio']
                request.user.save()
                messages.success(
                    request, 'تم الحفظ بنجاح', extra_tags='pale-green w3-border')
                return render(request, 'user/profile.html', context={'form': form, 'view_title': f'رايكم في | { request.user.username }'})
            else:
                return render(request, 'user/profile.html', context={'form': form, 'view_title': f'رايكم في | { request.user.username }'})
        else:
            if request.user.id != id:
                profile = User.objects.prefetch_related('posts').get(id=id)
                return render(request, 'user/profile.html', {'profile': profile, 'view_title': f'رايكم في | { profile.username }', 'url_name': 'profile_view'})
            else:
                form = ProfileForm(instance=request.user,
                                use_required_attribute=False)
                return render(request, 'user/profile.html', {'form': form, 'view_title': f'رايكم في | { request.user.username }', 'url_name': 'profile_view'})
    except Exception as e:
        print("Exception ========>>>>>>>>> ",e)
        messages.success(
                    request, 'حدث خطأ ما يرجى المحاولة لاحقا', extra_tags='pale-red w3-border')
        return redirect('raykomfi:raykomfi-home')

@ratelimit(key='ip', rate='10/m', block=True)
def sign_in_view(request):
    try:
        if request.method == 'POST':
            goto_next = request.POST.get('next')
            form = SigninForm(request.POST, use_required_attribute=False)
            if form.is_valid():
                username = request.POST.get('email')
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
                        if goto_next:
                            return HttpResponseRedirect(goto_next)
                        else:
                            return HttpResponseRedirect(reverse('raykomfi:raykomfi-home'))
                else:
                    messages.success(
                        request, 'البريد الإكتروني أو كلمة المرور خاطئة', extra_tags='pale-red w3-border')
                    form = SigninForm(use_required_attribute=False)
                    return render(request, 'user/signin.html', context={'form': form, 'view_title': f'منصة رايكم في | تسجيل الدخول'})
            else:
                return render(request, 'user/signin.html', context={'form': form, 'view_title': f'منصة رايكم في | تسجيل الدخول'})
        else:
            form = SigninForm(use_required_attribute=False)
            context = {'form': form, 'view_title': f'رايكم في | تسجيل الدخول', 'url_name': 'signin_view'}
            if request.user.is_anonymous and 'next' in request.GET:
                messages.success(
                    request, 'يجب عليك تسجيل الدخول أولا', extra_tags='pale-yellow w3-border')
                context['next'] = request.GET.get('next')
            if request.user.is_authenticated:
                messages.success(
                    request, 'أنت مسجل الدخول بالفعل', extra_tags='pale-green w3-border')
                return redirect('/')
            return render(request, 'user/signin.html', context=context)
    except Exception as e:
        print("Exception ========>>>>>>>>> ",e)
        messages.success(
                    request, 'حدث خطأ ما يرجى المحاولة لاحقا', extra_tags='pale-red w3-border')
        return redirect('raykomfi:raykomfi-home')

@ratelimit(key='ip', rate='10/m', block=True)
def user_logout(request):
    try:
        logout(request)
        messages.success(
            request, 'تم تسجيل الخروج', extra_tags='pale-green w3-border')
        return HttpResponseRedirect('/user/signin/')
    except Exception as e:
        print("Exception ========>>>>>>>>> ", e)
        messages.success(
                    request, 'حدث خطأ ما يرجى المحاولة لاحقا', extra_tags='pale-red w3-border')
        return redirect('raykomfi:raykomfi-home')

@ratelimit(key='ip', rate='10/m', block=True)
def sign_up_view(request):
    try:
        if request.method == 'POST':
            form = SignupForm(request.POST, use_required_attribute=False)

            if form.is_valid():
                token = secrets.token_hex(20)
                user = form.save(commit=False)
                user.verification_code = token
                current_date_and_time =timezone.now()
                hours_added = timezone.timedelta(hours=1)
                user.verification_code_expire = current_date_and_time + hours_added
                user.save()
                current_site = get_current_site(request)
                mail_subject = 'تفعيل حسابك على رايكم في'
                to_email = form.cleaned_data.get('email')
                from_email = 'no-reply@raykomfi.com'
                template="user/acc_activate_email.html"
                html_email_template = get_template(template).render(
                    {
                        'site': SimpleLazyObject(lambda: get_current_site(request)),
                        'user': user,
                        'uid': user.id,
                        'token': token
                    }
                )
                # send email
                send_email(html_email_template=html_email_template, mail_subject=mail_subject, to_email=to_email, from_email=from_email, token=token)
                messages.success(
                    request, 'تم انشاء الحساب, يرجى مراجعة بريدك الالكتروني لتفعيل حسابك', extra_tags='pale-green w3-border')

                return HttpResponseRedirect('/user/signin')

            else:
                return render(request, 'user/register.html', context={'form': form, 'view_title': f'منصة رايكم في | حساب جديد'})

        else:
            form = SignupForm(use_required_attribute=False)
            return render(request, 'user/register.html', context={'form': form, 'url_name': 'signup_view', 'view_title': f'منصة رايكم في | حساب جديد'})
    except Exception as e:
        print("Exception ========>>>>>>>>> ", e)
        messages.success(
                    request, 'حدث خطأ ما يرجى المحاولة لاحقا', extra_tags='pale-red w3-border')
        return redirect('raykomfi:raykomfi-home')

@ratelimit(key='ip', rate='10/m', block=True)
def sign_up_with_no_registration_view(request):
    try:
        if request.method == 'POST':
            form = SignupWithNoRegistrationForm(request.POST, use_required_attribute=False)

            if form.is_valid():
                token = secrets.token_hex(4)
                user = form.save(commit=False)
                current_date_and_time = timezone.now()
                current_site = get_current_site(request)
                mail_subject = 'رمز المشاركة على رايكم في'
                to_email = form.cleaned_data.get('email')
                email_name = to_email.split('@')[0]
                token = f'{email_name}-{token}'
                user.code = token
                user.save()
                from_email = 'no-reply@raykomfi.com'
                template="user/no_registration_code_email.html"
                html_email_template = get_template(template).render(
                    {
                        'token': token
                    }
                )
                # send email
                send_email(html_email_template=html_email_template, mail_subject=mail_subject, to_email=to_email, from_email=from_email, token=token)
                messages.success(
                    request, 'تم إرسال رمز المشاركة إلى بريدك الإلكتروني', extra_tags='pale-green w3-border')

                return HttpResponseRedirect('/')

            else:
                return render(request, 'user/user_with_no_registration.html', context={'form': form, 'view_title': f'منصة رايكم في | طلب رمز المشاركة'})

        else:
            form = SignupWithNoRegistrationForm(use_required_attribute=False)
            return render(request, 'user/user_with_no_registration.html', context={'form': form, 'view_title': f'منصة رايكم في | طلب رمز المشاركة'})
    except Exception as e:
        print("Exception ========>>>>>>>>> ", e)
        messages.success(
                    request, 'حدث خطأ ما يرجى المحاولة لاحقا', extra_tags='pale-red w3-border')
        return redirect('raykomfi:raykomfi-home')

@ratelimit(key='ip', rate='10/m', block=True)
def forgot_no_registration_code(request):
    try:
        if request.method == 'POST':
            form = ForgotNoRegistrationCodeForm(request.POST, use_required_attribute=False)

            if form.is_valid():
                to_email = form.cleaned_data.get('email')
                obj = NoRegistrationCode.objects.filter(email=to_email).first()
                if not obj:
                    messages.success(
                    request, 'يرجى طلب رمز مشاركة جديد', extra_tags='pale-green w3-border')

                    return HttpResponseRedirect('/')

                token = obj.code
                from_email = 'no-reply@raykomfi.com'
                mail_subject = 'رمز المشاركة على رايكم في'
                template="user/no_registration_code_email.html"
                html_email_template = get_template(template).render(
                    {
                        'token': token
                    }
                )
                # send email
                send_email(html_email_template=html_email_template, mail_subject=mail_subject, to_email=to_email, from_email=from_email, token=token)
                messages.success(
                    request, 'تم إرسال رمز المشاركة إلى بريدك الإلكتروني', extra_tags='pale-green w3-border')

                return HttpResponseRedirect('/')

            else:
                return render(request, 'user/forgot_no_registration_code.html', context={'form': form, 'view_title': f'منصة رايكم في | طلب رمز المشاركة'})

        else:
            form = ForgotNoRegistrationCodeForm(use_required_attribute=False)
            return render(request, 'user/forgot_no_registration_code.html', context={'form': form, 'view_title': f'منصة رايكم في | طلب رمز المشاركة'})
    except Exception as e:
        print("Exception ========>>>>>>>>> ", e)
        messages.success(
                    request, 'حدث خطأ ما يرجى المحاولة لاحقا', extra_tags='pale-red w3-border')
        return redirect('raykomfi:raykomfi-home')


@login_required
@ratelimit(key='ip', rate='50/m', block=True)
def delete_user(request, id):
    try:
        user = User.objects.get(id=id)
        question = request.GET['question']
        if question != 'true':
            rand_num = randint(100000, 999999)
            user.is_active = False
            user.first_name = ""
            user.last_name = ""
            user.email = f"{rand_num}@delete_user.com"
            user.username = f"{rand_num}_deleted_user"
            user.save()
            messages.success(
                    request, 'تم حذف حسابك, لكن إستفساراتك, تعليقاتك و ردودك ستبقى لكن بدون إسمك الشخصي.', extra_tags='pale-green w3-border')
            return redirect('raykomfi:user-signin')
        else:
            return render(request, 'sections/are_you_sure.html')
    except Exception as e:
        print("Exception ========>>>>>>>>> ", e)
        messages.success(
                    request, 'حدث خطأ ما يرجى المحاولة لاحقا', extra_tags='pale-red w3-border')
        return redirect('raykomfi:raykomfi-home')

@ratelimit(key='ip', rate='10/m', block=True)
def post_view(request, id, slug):
    try:

        post = Post.objects.select_related('creator', 'category').filter(Q(id__exact=id)).first()

        if not post:
            messages.success(
                    request, 'ما تبحث عنه غير موجود', extra_tags='pale-red w3-border')
            return redirect('raykomfi:raykomfi-home')

        comments_count = 0
        if request.get_raw_uri().find('all_comments') < 0:
            comments_count =  Post.objects.select_related('creator', 'category').filter(id__exact=id).first().comments.count()
            post_comments = Comment.objects.filter(post__id=id)[:5]
        else:
            post_comments = Comment.objects.filter(post__id=id)
        

        if post.isActive == False:
            if request.user.id == None:
                messages.success(
                    request, 'تتم مراجعة الإستفسار الان, سيتم نشر إستفسارك قريبا, إذا لم تجد إستفسارك نشر خلال 24 ساعة هذا يعني أنه مخالف', extra_tags='pale-green w3-border')
                return redirect('raykomfi:raykomfi-home')
            if request.user and not request.user.is_staff and request.user.id != post.creator.id:
                return redirect('raykomfi:raykomfi-home')

        rand_ids = Post.objects.select_related('creator', 'category').filter(category=post.category).values_list('id', flat=True)
        related_posts = []
        if len(rand_ids) > 6:
            rand_ids = list(rand_ids)
            rand_ids = sample(rand_ids, 6)
            related_posts = Post.objects.select_related('creator', 'category').filter(id__in=rand_ids)
        comment_form = CommentForm()
        reply_form = ReplyForm()
        if request.GET.get('read'):
            full_path = request.get_full_path()
            notis = Notification.objects.filter(description__icontains=full_path)
            if notis: 
                notis.first().delete()

        context = {'post': post, 'comment_form': comment_form, 'reply_form': reply_form, 'related_posts': related_posts, 'comments_count': comments_count, 'post_comments': post_comments, 'view_title': f'رايكم في | { post.title }', 'url_name': 'post_view'}

        # hitcount logic
        hit_count = get_hitcount_model().objects.get_for_object(post)
        hits = hit_count.hits
        hitcontext = context['hitcount'] = {'pk': hit_count.pk}
        hit_count_response = HitCountMixin.hit_count(request, hit_count)
        if hit_count_response.hit_counted:
            hits = hits + 1
            hitcontext['hit_counted'] = hit_count_response.hit_counted
            hitcontext['hit_message'] = hit_count_response.hit_message
            hitcontext['total_hits'] = hits

        return render(request, 'sections/post_view.html', context=context)
    except Exception as e:
        print("Exception ========>>>>>>>>> ", e)
        messages.success(
                    request, 'حدث خطأ ما يرجى المحاولة لاحقا', extra_tags='pale-red w3-border')
        return redirect('raykomfi:raykomfi-home')


@ login_required
@ratelimit(key='ip', rate='10/m', block=True)
def my_posts_view(request, user_id):
    try:
        posts = Post.objects.prefetch_related('creator', 'category', 'comments').filter(creator__id=user_id)[:5]
        count = Post.objects.prefetch_related('creator', 'category', 'comments').filter(creator__id=user_id).count()
        return render(request, 'sections/user_posts.html', context={'posts': posts, 'count_posts': count, 'view_title': f'منصة رايكم في | إستفساراتي'})
    except Exception as e:
        print("Exception ========>>>>>>>>> ", e)
        messages.success(
                    request, 'حدث خطأ ما يرجى المحاولة لاحقا', extra_tags='pale-red w3-border')
        return redirect('raykomfi:raykomfi-home')

@ login_required
@ratelimit(key='ip', rate='10/m', block=True)
def my_comments_view(request, user_id):
    try:
        comments = Comment.objects.prefetch_related('user', 'replies').filter(user__id=user_id).order_by('-created')[:5]
        count = Comment.objects.prefetch_related('user', 'replies').filter(user__id=user_id).count()
        return render(request, 'sections/user_comments.html', context={'comments': comments, 'count_comments': count, 'view_title': f'منصة رايكم في | آرائي'})
    except Exception as e:
        print("Exception ========>>>>>>>>> ", e)
        messages.success(
                    request, 'حدث خطأ ما يرجى المحاولة لاحقا', extra_tags='pale-red w3-border')
        return redirect('raykomfi:raykomfi-home')

@ login_required
@ratelimit(key='ip', rate='10/m', block=True)
def my_comments_most_replied_view(request, user_id):
    try:
        comments = Comment.objects.prefetch_related('user', 'replies').filter(user__id=user_id).annotate(replies_count=Count('replies')).order_by('-replies_count')
        count = 0
        return render(request, 'sections/user_comments.html', context={'comments': comments, 'count_comments': count, 'view_title': f'منصة رايكم في | آرائي الأكثر ردا'})
    except Exception as e:
        print("Exception ========>>>>>>>>> ", e)
        messages.success(
                    request, 'حدث خطأ ما يرجى المحاولة لاحقا', extra_tags='pale-red w3-border')
        return redirect('raykomfi:raykomfi-home')

@ login_required
@ratelimit(key='ip', rate='50/m', block=True)
def my_comments_most_voted_view(request, user_id):
    try:
        comments = Comment.objects.prefetch_related('user', 'replies').filter(user__id=user_id).order_by('-votes')
        count = 0
        return render(request, 'sections/user_comments.html', context={'comments': comments, 'count_comments': count, 'view_title': f'منصة رايكم في | آرائي الأكثر تصويتا'})
    except Exception as e:
        print("Exception ========>>>>>>>>> ", e)
        messages.success(
                    request, 'حدث خطأ ما يرجى المحاولة لاحقا', extra_tags='pale-red w3-border')
        return redirect('raykomfi:raykomfi-home')




@ login_required
@ratelimit(key='ip', rate='10/m', block=True)
def post_edit(request, id, slug):
    try:
        instance = get_object_or_404(Post, id=id, slug=slug)
        if request.method == 'POST':
            form = NewPostForm(request.POST or None, request.FILES or None, instance=instance,
                            use_required_attribute=False)
            if form.is_valid():
                obj = form.save(commit=False)
                obj.isActive = False
                obj.save()
                instance = get_object_or_404(Post, id=id)
                return render(request, 'sections/post_view.html', context={'form': form, 'post': instance, 'view_title': f'رايكم في | {instance.title}'})
            else:
                return render(request, 'sections/edit_post.html', context={'form': form, 'post': instance, 'view_title': f'رايكم في | {instance.title}'})
        else:
            post = Post.objects.get(Q(id__exact=id) & Q(slug__exact=slug))
            form = NewPostForm(instance=instance, use_required_attribute=False)
            return render(request, 'sections/edit_post.html', context={'form': form, 'post': post, 'view_title': f'رايكم في | {post.title}'})
    except Exception as e:
        print("Exception ========>>>>>>>>> ", e)
        messages.success(
                    request, 'حدث خطأ ما يرجى المحاولة لاحقا', extra_tags='pale-red w3-border')
        return redirect('raykomfi:raykomfi-home')


@ login_required
@ratelimit(key='ip', rate='10/m', block=True)
def create_post(request):
    try:
        if request.method == 'POST':
            form = NewPostForm(request.POST or None, request.FILES or None,
                            use_required_attribute=False)
            if form.is_valid():
                post = form.save(commit=False)
                post.creator = request.user
                post.save()
                return redirect(post.get_absolute_url())
            else:
                return render(request, 'sections/create_post.html', context={'form': form, 'view_title': f'منصة رايكم في | إستفسار جديد'})
        else:
            form = NewPostForm(use_required_attribute=False)
            return render(request, 'sections/create_post.html', context={'form': form, 'view_title': f'منصة رايكم في | إستفسار جديد', 'url_name': 'ask_people_view'})
    except Exception as e:
        print("Exception ========>>>>>>>>> ", e)
        messages.success(
                    request, 'حدث خطأ ما يرجى المحاولة لاحقا', extra_tags='pale-red w3-border')
        return redirect('raykomfi:raykomfi-home')

@ratelimit(key='ip', rate='10/m', block=True)
def create_post_with_no_registration(request):
    try:
        if request.method == 'POST':
            form = NewPostWithNoRegistrationForm(request.POST or None, request.FILES or None,
                            use_required_attribute=False)
            if form.is_valid():
                code = form.cleaned_data['code']
                post = form.save(commit=False)
                post.creator = None
                post.save()
                return redirect(post.get_absolute_url())
            else:
                return render(request, 'sections/create_post_with_no_registration.html', context={'form': form, 'view_title': f'منصة رايكم في | إستفسار جديد'})
        else:
            form = NewPostWithNoRegistrationForm(use_required_attribute=False)
            return render(request, 'sections/create_post_with_no_registration.html', context={'form': form, 'view_title': f'منصة رايكم في | إستفسار جديد', 'url_name': 'ask_people_view'})
    except Exception as e:
        print("Exception ========>>>>>>>>> ", e)
        messages.success(
                    request, 'حدث خطأ ما يرجى المحاولة لاحقا', extra_tags='pale-red w3-border')
        return redirect('raykomfi:raykomfi-home')

@login_required
@ratelimit(key='ip', rate='50/m', block=True)
def change_password_view(request):
    try:
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
                    'form': form, 'view_title': f'رايكم في | تغيير كلمة المرور'
                })
        else:
            form = CustomChangePasswordForm(
                request.user, use_required_attribute=False)
            return render(request, 'user/change_password.html', {
                'form': form, 'view_title': f'رايكم في | تغيير كلمة المرور'
            })
    except Exception as e:
        print("Exception ========>>>>>>>>> ", e)
        messages.success(
                    request, 'حدث خطأ ما يرجى المحاولة لاحقا', extra_tags='pale-red w3-border')
        return redirect('raykomfi:raykomfi-home')

@ratelimit(key='ip', rate='10/m', block=True)
def restore_password_view(request):
    try:
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
                        'user': user,
                        'view_title': f'منصة رايكم في | إعادة تعيين كلمة المرور'
                    })
            else:
                return redirect('raykomfi:user-signin')
    except Exception as e:
        print("Exception ========>>>>>>>>> ", e)
        messages.success(
                    request, 'حدث خطأ ما يرجى المحاولة لاحقا', extra_tags='pale-red w3-border')
        return redirect('raykomfi:raykomfi-home')

@ratelimit(key='ip', rate='10/m', block=True)
def forgot_password_view(request):
    try:
        if request.method == 'POST':
            form = CustomPasswordResetForm(request.POST ,use_required_attribute=False)
            if form.is_valid():
                token = secrets.token_hex(20)
                user = get_object_or_404(User, email=form.cleaned_data['email'])
                user.verification_code = token
                current_date_and_time =timezone.now()
                hours_added = timezone.timedelta(hours=1)
                user.verification_code_expire = current_date_and_time + hours_added
                user.save()
                current_site = get_current_site(request)
                mail_subject = 'رابط تغيير كلمة المرور'
                to_email = form.cleaned_data.get('email')
                from_email = 'no-reply@raykomfi.com'
                # Send data to email template and get email template.
                html_email_template = get_template("user/restore_password_email_view.html").render(
                    {
                        'site': SimpleLazyObject(lambda: get_current_site(request)),
                        'user': user,
                        'uid': user.id,
                        'token': token
                    }
                )
                # send email
                send_email(html_email_template=html_email_template, mail_subject=mail_subject, to_email=to_email, from_email=from_email, token=token)
                messages.success(
                    request, 'تم إرسال رابط إعادة تعيين كلمة المرور إلى بريدك الإلكتروني', extra_tags='pale-green w3-border')

                return HttpResponseRedirect('/user/signin')
            else:
                return render(request, 'user/forgot_password.html', context={'form': form, 'view_title': f'منصة رايكم في | نسيت كلمة المرور'})
        else:
            form = CustomPasswordResetForm(use_required_attribute=False)
            return render(request, 'user/forgot_password.html', context={'form': form, 'view_title': f'منصة رايكم في | نسيت كلمة المرور'})
    except Exception as e:
        print("Exception ========>>>>>>>>> ", e)
        messages.success(
                    request, 'حدث خطأ ما يرجى المحاولة لاحقا', extra_tags='pale-red w3-border')
        return redirect('raykomfi:raykomfi-home')

@login_required
@ratelimit(key='ip', rate='10/m', block=True)
def change_email_view(request):
    try:
        if request.method == 'POST':
            form = ChangeEmailForm(request.POST, request=request ,use_required_attribute=False)
            if form.is_valid():
                token = secrets.token_hex(20)
                user = get_object_or_404(User, email=form.cleaned_data['current_email'])
                user.verification_code = token
                current_date_and_time =timezone.now()
                hours_added = timezone.timedelta(hours=1)
                user.verification_code_expire = current_date_and_time + hours_added
                user.save()
                current_site = get_current_site(request)
                mail_subject = 'تأكيد البريد الإلكتروني'
                to_email = form.cleaned_data.get('new_email2')
                from_email = 'no-reply@raykomfi.com'
                # Send data to email template and get email template.
                html_email_template = get_template("user/change_email_email_view.html").render(
                    {
                        'site': SimpleLazyObject(lambda: get_current_site(request)),
                        'user': user,
                        'uid': user.id,
                        'token': token,
                        'new_email': to_email
                    }
                )
                # send email
                send_email(html_email_template=html_email_template, mail_subject=mail_subject, to_email=to_email, from_email=from_email, token=token)
                messages.success(
                    request, 'تم إرسال رابط  تأكيد البريد الإلكتروني إلى بريدك الإلكتروني الجديد', extra_tags='pale-green w3-border')

                return HttpResponseRedirect('/')
            else:
                return render(request, 'user/change_email.html', context={'form': form, 'view_title': f'منصة رايكم في | تغيير البريد الإلكتروني'})
        else:
            form = ChangeEmailForm(use_required_attribute=False, request=request)
            return render(request, 'user/change_email.html', context={'form': form, 'view_title': f'منصة رايكم في | تغيير البريد الإلكتروني'})
    except Exception as e:
        print("Exception ========>>>>>>>>> ", e)
        messages.success(
                    request, 'حدث خطأ ما يرجى المحاولة لاحقا', extra_tags='pale-red w3-border')
        return redirect('raykomfi:raykomfi-home')

@login_required
@ratelimit(key='ip', rate='50/m', block=True)
def confirm_new_email(request, uid, token, new_email):
    try:
        user = User.objects.get(id=uid)
        current_date_and_time = timezone.now()
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and current_date_and_time < user.verification_code_expire and user.verification_code == token:
        user.email = new_email
        user.save()
        logout(request)
        messages.success(
            request, 'تم تغيير بريدك الإلكتروني بنجاح', extra_tags='pale-green w3-border')
        return redirect('raykomfi:user-signin')
    else:
        logout(request)
        messages.success(
                request, 'رابط غير صالح, أعد المحاولة', extra_tags='pale-red w3-border')
        return redirect('raykomfi:user-signin')

@login_required
@ratelimit(key='ip', rate='50/m', block=True)
def messages_view(request, user_id, message_id=0):
    try:
        if request.method == 'POST':
            message = get_object_or_404(Message, id=message_id)
            message.is_read = True
            message.save()
            user_messages = Message.objects.filter(receiver__exact=user_id)
            return render(request, 'sections/messages.html', {'user_messages': user_messages, 'fetched_message': message, 'view_title': f'منصة رايكم في | الرسائل'})
        else:
            if message_id != 0:
                message = get_object_or_404(Message, id=message_id)
                message.is_read = True
                message.save()
                user_messages = Message.objects.filter(receiver__exact=user_id)
                Notification.objects.filter(description=request.path).first().delete()
                return render(request, 'sections/messages.html', {'user_messages': user_messages, 'fetched_message': message, 'view_title': f'منصة رايكم في | الرسائل', 'url_name': 'message_view'})
            user_messages = Message.objects.filter(receiver__id__exact=user_id)
            return render(request, 'sections/messages.html', {'user_messages': user_messages, 'view_title': f'منصة رايكم في | الرسائل', 'url_name': 'message_view'})
    except Exception as e:
        print("Exception ========>>>>>>>>> ", e)
        messages.success(
                    request, 'حدث خطأ ما يرجى المحاولة لاحقا', extra_tags='pale-red w3-border')
        return redirect('raykomfi:raykomfi-home')
        
@login_required
@ratelimit(key='ip', rate='50/m', block=True)
def new_message_view(request, code):
    try:
        receiver = get_object_or_404(User, uuid=code)
        if request.method == 'POST':
            form = MessageForm(
                request.POST, use_required_attribute=False)
            if form.is_valid():
                message = Message.objects.create(user=request.user, receiver=receiver, title=form.cleaned_data['title'], content=form.cleaned_data['content'])
                messages.success(
                request, f'تم إرسال الرسالة الى {receiver.username} بنجاح', extra_tags='pale-green w3-border')
                if receiver.id != request.user.id:
                    notify.send(request.user, recipient=receiver ,action_object=message, description=message.get_noti_url(), target=message, verb='message')
                return redirect(receiver.get_absolute_url())
            else:
                return render(request, 'sections/new_message.html', context={'form': form, 'receiver': receiver, 'view_title': f'منصة رايكم في | رسالة جديدة'})
        else:
            form = MessageForm(use_required_attribute=False)
            return render(request, 'sections/new_message.html', context={'form': form, 'receiver': receiver, 'view_title': f'منصة رايكم في | رسالة جديدة'})
    except Exception as e:
        print("Exception ========>>>>>>>>> ", e)
        messages.success(
                    request, 'حدث خطأ ما يرجى المحاولة لاحقا', extra_tags='pale-red w3-border')
        return redirect('raykomfi:raykomfi-home')
    


@login_required
@ratelimit(key='ip', rate='50/m', block=True)
def add_comment(request, post_id):
    try:
        comment_form = CommentForm(request.POST or None)
        post = Post.objects.prefetch_related(
            'comments').prefetch_related('comments__replies').get(id__exact=post_id)
        if comment_form.is_valid():
            comment = Comment.objects.create(
                content=comment_form.cleaned_data['content'], user=request.user, post=post)
            messages.success(
                request, 'تم إضافة رأيك بنجاح', extra_tags='pale-green w3-border')
            return HttpResponseRedirect(post.get_absolute_url())
        else:
            return render(request, 'sections/post_view.html', {'post': post, 'comment_form': comment_form})
    except Exception as e:
        print("Exception ========>>>>>>>>> ", e)
        messages.success(
                    request, 'حدث خطأ ما يرجى المحاولة لاحقا', extra_tags='pale-red w3-border')
        return redirect('raykomfi:raykomfi-home')



@login_required
@ratelimit(key='ip', rate='50/m', block=True)
def comment_vote(request, comment_id):
    try:
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
    except Exception as e:
        print("Exception ========>>>>>>>>> ", e)
        messages.success(
                    request, 'حدث خطأ ما يرجى المحاولة لاحقا', extra_tags='pale-red w3-border')
        return redirect('raykomfi:raykomfi-home')

@login_required
@ratelimit(key='ip', rate='50/m', block=True)
def add_reply(request, post_id, comment_id):
    try:
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
    except Exception as e:
        print("Exception ========>>>>>>>>> ", e)
        messages.success(
                    request, 'حدث خطأ ما يرجى المحاولة لاحقا', extra_tags='pale-red w3-border')
        return redirect('raykomfi:raykomfi-home')

def activate(request, uid, token):
    try:
        user = User.objects.get(id=uid)
        current_date_and_time = timezone.now()
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and current_date_and_time < user.verification_code_expire and user.verification_code == token:
        if user.email_active == True:
            messages.success(
            request, 'حسابك مفعل من قبل', extra_tags='pale-green w3-border')
            return redirect('raykomfi:user-signin')
        user.email_active = True
        user.verification_code = ""
        user.verification_code_expire = None
        user.save()
        logout(request)
        messages.success(
            request, 'تم تفعيل حسابك, يمكنك الان استخدام المنصة', extra_tags='pale-green w3-border')
        return redirect('raykomfi:user-signin')
    else:
        return render(request, 'user/activate_fail.html')

@ratelimit(key='ip', rate='50/m', block=True)
def restore_password(request, uid, token):
    try:
        user = User.objects.get(id=uid)
        current_date_and_time = timezone.now()
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and current_date_and_time < user.verification_code_expire and user.verification_code == token:
        user.verification_code = ""
        user.verification_code_expire = None
        user.save()
        form = RestorePasswordForm(use_required_attribute=False)
        return render(request, 'user/restore_password.html', {'form': form, 'user': user})
    else:
        messages.success(
                request, 'رابط غير صالح, أعد المحاولة', extra_tags='pale-red w3-border')
        return redirect('raykomfi:user-signin')

@ratelimit(key='ip', rate='50/m', block=True)
def send_link(request):
    if request.method == 'POST':
        try:
            token = secrets.token_hex(20)
            email = request.POST.get('email')
            if email.find('@') == -1:
                messages.success(
                    request, 'أدخل بريد إلكتروني صحيح, أعد المحاولة مرة أخرى', extra_tags='pale-red w3-border')
                return redirect('raykomfi:user-signin')
            to_email = email
            user = get_object_or_404(User, email=to_email)
            if user.email_active == True or not user:
                messages.success(
                    request, 'البريد الألكتروني مفعل أو حدث خطأ ما يرجى المحاولة لاحقا', extra_tags='pale-red w3-border')
                return redirect('raykomfi:user-signin')
            user.verification_code = token
            current_date_and_time =timezone.now()
            hours_added = timezone.timedelta(hours=1)
            user.verification_code_expire = current_date_and_time + hours_added
            user.save()
            mail_subject = 'تفعيل حسابك على رايكم في'
            from_email = 'no-reply@raykomfi.com'
            # Send data to email template and get email template.
            html_email_template = get_template("user/acc_activate_email.html").render(
                {
                    'site': SimpleLazyObject(lambda: get_current_site(request)),
                    'user': user,
                    'uid': user.id,
                    'token': token
                }
            )
            # send email
            send_email(html_email_template=html_email_template, mail_subject=mail_subject, to_email=to_email, from_email=from_email, token=token)
            messages.success(
                request, 'تم إرسال رابط التفعيل الى بريدك الإلكتروني', extra_tags='pale-green w3-border')
            return HttpResponseRedirect(reverse('raykomfi:user-signin'))
        except Exception as e:
            print("Exception ========>>>>>>>>> ", e)
            messages.success(
                    request, 'حدث خطأ ما يرجى المحاولة لاحقا', extra_tags='pale-red w3-border')
            return redirect('raykomfi:user-signin')
        

    else:
        return render(request, 'user/activate_account.html')

@ratelimit(key='ip', rate='50/m', block=True)
def privacy_policy_view(request):
    return render(request, 'sections/privacy_policy.html', {'view_title': 'منصة رايكم في | سياسة الخصوصية والإستخدام'})

@ratelimit(key='ip', rate='50/m', block=True)
def about_view(request):
    return render(request, 'sections/about.html', {'view_title': 'منصة رايكم في | عن منصة رايكم في'})

@ratelimit(key='ip', rate='50/m', block=True)
def not_found_handler(request):
    return JsonResponse({'message': ''}, status=status.HTTP_404_NOT_FOUND)

def suspicious_limit(request , exception=None):
    print('LimitedError:', 'with ip', request.META.get('X-Real-IP'))
    return JsonResponse({'message': 'Sorry, you are blocked'}, status=status.HTTP_429_TOO_MANY_REQUESTS)

@require_GET
@ratelimit(key='ip', rate='50/m', block=True)
def robots_txt(request):
    lines = [
        "User-Agent: *",
        "Disallow: /user/profile/",
        "Disallow: /admin/",
        ]
    return HttpResponse("\n".join(lines), content_type="text/plain")