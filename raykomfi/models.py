# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import AbstractUser
from django_countries.fields import CountryField
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django import forms
from django_resized import ResizedImageField
from cloudinary.models import CloudinaryField
from uuid import uuid4, uuid1
from django.core.validators import MinValueValidator, MaxValueValidator


from django.core.cache import cache 
from datetime import datetime
from datetime import timedelta
from django.conf import settings
from django_countries.fields import CountryField
from api.models import Hashtags

from hitcount.models import HitCountMixin, HitCount
from django.contrib.contenttypes.fields import GenericRelation
from tinymce.models import HTMLField
from notifications.signals import notify
from twitter import *
import facebook
from dotenv import load_dotenv
load_dotenv()
import os
import pytz
import re
from summa import keywords
import requests
import json
import arrow
from .utils import write_into_instgram_image
from instabot import Bot 
from shutil import rmtree
utc=pytz.UTC

BASE_URL = 'https://www.raykomfi.com' if os.getenv('environment') == 'prod' else 'http://localhost:8000'




def slugify(str):
    str = str.replace(" ", "-")
    str = str.replace(",", "-")
    str = str.replace("(", "-")
    str = str.replace(")", "")
    str = str.replace("؟", "")
    return str

def natural_time(targeted_object):
    return arrow.get(targeted_object).humanize(locale='ar')

class User(AbstractUser):
    bio = models.TextField(blank=True, verbose_name='نبذة عن',)
    profile_image = models.CharField(max_length=255, blank=True, null=True, verbose_name='صورة شخصية', default='/media/profile_images/0.png')
    country = models.CharField(max_length=255, verbose_name='الدولة', blank=True)
    isBlocked = models.BooleanField(default=False, verbose_name='محظور؟')
    uuid = models.UUIDField(default=uuid4, editable=False, verbose_name='رمز العضو', null=True)
    secret_code = models.UUIDField(default=uuid1, editable=False, verbose_name='رمز العمليات', null=True)
    email_active = models.BooleanField(
        default=False, verbose_name='ايميل مفعل')
    stay_logged_in = models.BooleanField(
        default=False, verbose_name='البقاء متصلا')
    email = models.EmailField(unique=True, verbose_name='بريد الإلكتروني',)
    get_notifications = models.BooleanField(
        default=True, verbose_name='إستقبال إشعارات ؟')
    hide_name = models.BooleanField(
        default=True, verbose_name='إظهارالإسم ؟')
    allow_messages = models.BooleanField(
        default=True, verbose_name='إستقبال رسائل ؟')
    verification_code = models.CharField(max_length=255, blank=True, null=True, verbose_name='رمز العمليات')
    verification_code_expire = models.DateTimeField(blank=True, null=True, verbose_name='تاريخ إنتهاء رمز العمليات')
    last_time_best_user = models.DateTimeField(blank=True, null=True, verbose_name='اخر مرة حصل على عضو الشهر')
    user_trust = models.FloatField(validators=[MaxValueValidator(6.0), MinValueValidator(0.0)], default=0.0, verbose_name='قوة الرأي')
    accepted_conditions_terms = models.BooleanField(default=False)
    continent = models.CharField(max_length=155, default='')
    is_deleted = models.BooleanField(default=False, verbose_name='حساب محذوف؟')


    def get_absolute_url(self):
        return reverse('raykomfi:user-profile', args=[self.id])

    def online(self):
        if self.last_login:
            now = datetime.now()
            last_seen = cache.get(f'seen_{self.username}')
            if not last_seen:
                return False

            if last_seen.replace(microsecond = 0).replace(tzinfo=None) > now.replace(microsecond = 0) - timedelta(seconds=38):
                return True
            else:
                return False
        else:
            return False
    
    def last_seen(self):
        last_seen = cache.get(f'seen_{self.username}')

        if last_seen:
            return last_seen
        else:
            False

    def last_login_natural(self):
        return natural_time(self.last_login)

class Category(models.Model):

    name = models.CharField(
        max_length=200, verbose_name='اسم التصنيف', db_index=True)
    slug = models.CharField(
        max_length=200, db_index=True, unique=True, blank=True)

    class Meta:
        ordering = ("-name", )
        verbose_name = "تصنيف"
        verbose_name_plural = "تصنيفات"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('raykomfi:list_post_category', args=[self.slug])

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)


class Post(models.Model, HitCountMixin):
    creator = models.ForeignKey(User, related_name='posts', verbose_name='الكاتب',  on_delete=models.SET_DEFAULT, default=None, null=True, blank=True, db_index=True)
    creator_image = models.CharField(max_length=255, verbose_name='صورة الكاتب', blank=True, null=True, default='/media/profile_images/0.png')
    country = models.CharField(max_length=255, verbose_name='دولة الكاتب', blank=True, null=True, default='')
    category = models.ForeignKey(Category, verbose_name='التصنيف', null=True, on_delete=models.SET_DEFAULT, default=None, db_index=True)
    title = models.CharField(
        max_length=200, verbose_name='الموضوع', db_index=True)
    slug = models.CharField(
        max_length=200, db_index=True, null=True, blank=True)
    content = HTMLField(verbose_name='نبذة عن الإستفسار', blank=True, db_index=True)
    isActive = models.BooleanField(default=False, db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    hit_count_generic = GenericRelation(HitCount, object_id_field='object_pk', related_query_name='hit_count_generic_relation')
    keywords = models.CharField(max_length=255, blank=True, null=True)
    is_uploaded_on_social = models.BooleanField(default=False)

    class Meta:
        ordering = ('-created', )
        index_together = (('id', 'slug'), )
        verbose_name = "منشور"
        verbose_name_plural = "منشورات"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('raykomfi:post-view', args=[self.id, self.slug])

    def get_image_url(self):
        return self.image.url

    def get_noti_url(self):
        return reverse('raykomfi:post-view', args=[self.id, self.slug]) + f'?read={self.id}'
    
    def get_twitter_url(self):
        return BASE_URL + reverse('raykomfi:post-view', args=[self.id, self.slug])

    def get_created_natural(self):
        return natural_time(self.created)

    def get_updated_natural(self):
        return natural_time(self.updated)


    def save(self, *args, **kwargs):
        # When post gets accepted
        prev_post_status = Post.objects.filter(pk=self.pk).first()
        if prev_post_status:
            if prev_post_status != self.isActive and self.isActive == True and os.getenv('environment') == 'prod' and self.is_uploaded_on_social == False:
                # Post to twitter and facebook
                try:
                    # headers = {
                    # 'Authorization': f'Bearer {os.getenv("bitly_token")}',
                    # 'Content-Type': 'application/json',
                    # }

                    # data = { "long_url": f"{self.get_twitter_url()}", "domain": "bit.ly", "group_guid": "BkcriP1cZcS" }

                    # response = requests.post('https://api-ssl.bitly.com/v4/shorten', headers=headers, data=json.dumps(data))
                    
                    # Post to twitter
                    t = Twitter(auth=OAuth(os.getenv('access_token'), os.getenv('access_token_secret'), os.getenv('consumer_key'), os.getenv('consumer_secret')))
                    t.statuses.update(status=f'{self.title} \n \n ☟ إفتح صفحة الإستفسار من هنا وشارك رأيك مع المستفسر  ☟  \n {self.get_twitter_url()} ', media_ids="")

                    # Post to instgram
                    bot = Bot()
                    bot.login(username = os.getenv('insta_username'),  password = os.getenv('insta_password'), is_threaded=True)
                    if len(self.title) > 60:
                        title = self.title[:60] + '...'
                    else:
                        title = self.title

                    write_into_instgram_image(title, text_size=len(self.title))
                    hashtags = Hashtags.objects.all().first()
                    bot.upload_photo("media/instgram/generated_post_image/output.jpg", caption=f'رابط الإستفسار {self.get_twitter_url()} \n \n {hashtags.hashtags}')
                    rmtree('./config')

                    # Post to facebook
                    token = os.getenv('fb_token')
                    fb = facebook.GraphAPI(access_token=token)
                    fb.put_object(parent_object='me', connection_name='feed', message=f'{self.title} \n \n ☟ إفتح صفحة الإستفسار من هنا وشارك رأيك مع المستفسر  ☟ \n {self.get_twitter_url()}')

                    self.is_uploaded_on_social = True
                except Exception as e:
                    print('=======================>', e)

                admin = User.objects.get(email=os.getenv('ADMIN_EMAIL'))
                anonymousUser = User.objects.filter(email="anonymous@anonymous.com").first()
                creator = self.creator
                if not self.creator:
                    creator = anonymousUser

                notify.send(admin, recipient=creator ,action_object=self, description=self.get_noti_url(), target=self, verb='post_accepted')
                super(Post, self).save(*args, **kwargs)
            else:
                super(Post, self).save(*args, **kwargs)
                
            # Generate slug
        self.slug = slugify(self.title)
        k = self.title
        clean1 = re.compile('<.*?>')
        clean2 = re.compile('[^A-Za-z0-9-\u0621-\u064A\u0660-\u0669 ]+')
        k = k.replace('nbsp', '')
        k = clean1.sub('', k)
        k = clean2.sub('', k)
        k = k.split(' ')
        final_keywords = []
        for keyword in k:
            if keyword in ["من", "على", "رايكم", "في", "الى", "عن", "منذ", "الذي", "اللي"]  or len(keyword) < 4:
                continue
            else:
                final_keywords.append(keyword)

        self.keywords = ','.join(final_keywords)
        super(Post, self).save(*args, **kwargs)
       
        

class Comment(models.Model):

    user = models.ForeignKey(
        User, related_name='my_comments', verbose_name='صاحب النعليق', on_delete=models.SET_DEFAULT, default=None, null=True, blank=True, db_index=True)
    user_image = models.CharField(max_length=255, verbose_name='صورة الكاتب', blank=True, null=True, default='/media/profile_images/0.png')
    country = models.CharField(max_length=255, verbose_name='دولة الكاتب', blank=True, null=True, default='')
    post = models.ForeignKey(
        Post, related_name='comments', verbose_name='المنشور', on_delete=models.CASCADE)
    content = models.TextField(verbose_name='التعليق', db_index=True)
    isActive = models.BooleanField(default=True, verbose_name='مفعل؟', db_index=True)
    votes = models.IntegerField(default=0)
    voted_like = models.ManyToManyField(
        User, related_name='comment_likes', verbose_name='الاعضاء المتفقين')
    voted_dislike = models.ManyToManyField(
        User, related_name='comment_dislikes', verbose_name='الاعضاء الغير متفقين')
    created = models.DateTimeField(
        auto_now_add=True, verbose_name='وقت اضافة التعليق', db_index=True)
    updated = models.DateTimeField(
        auto_now=True, verbose_name='وقت تحديث التعليق')

    class Meta:
        ordering = ('-user__user_trust','created')
        verbose_name = "تعليق"
        verbose_name_plural = "تعليقات"

    def __str__(self):
        return self.content

    def get_absolute_url(self):
        return reverse('raykomfi:post-view', args=[self.post.id, self.post.slug]) + f'#comment-id-{self.id}'

    def get_absolute_url_for_my_comments(self):
        return reverse('raykomfi:post-view', args=[self.post.id, self.post.slug]) + f'?all_comments=true' + f'#comment-id-{self.id}'

    def get_noti_url(self):
        return reverse('raykomfi:post-view', args=[self.post.id, self.post.slug]) + f'?all_comments=true' + f'&read={self.id}' + f'#comment-id-{self.id}'

    def get_created_natural(self):
        return natural_time(self.created)

    def get_updated_natural(self):
        return natural_time(self.updated)





class Reply(models.Model):

    user = models.ForeignKey(
        User, related_name='my_replies', verbose_name='صاحب النعليق', on_delete=models.SET_DEFAULT, default=None, null=True, blank=True, db_index=True)
    user_image = models.CharField(max_length=255, verbose_name='صورة الكاتب', blank=True, null=True, default='/media/profile_images/0.png')
    comment = models.ForeignKey(
        Comment, related_name='replies', verbose_name='التعليق', on_delete=models.CASCADE, db_index=True)
    content = models.TextField()
    isActive = models.BooleanField(default=True, verbose_name='مفعل؟')
    created = models.DateTimeField(
        auto_now_add=True, verbose_name='وقت اضافة التعليق', db_index=True)
    updated = models.DateTimeField(
        auto_now=True, verbose_name='وقت تحديث التعليق')

    class Meta:
        ordering = ('created', )
        verbose_name = "رد على تعليق"
        verbose_name_plural = "ردود على التعليقات"

    def __str__(self):
        return self.content

    def get_absolute_url(self):
        return reverse('raykomfi:post-view', args=[self.comment.post.id, self.comment.post.slug]) + f'#to-{self.id}'
    
    def get_noti_url(self):
        return reverse('raykomfi:post-view', args=[self.comment.post.id, self.comment.post.slug])+ f'?all_comments=true' + f'&read={self.id}' + f'#to-{self.id}'
    
    def get_created_natural(self):
        return natural_time(self.created)

    def get_updated_natural(self):
        return natural_time(self.updated)


class Message(models.Model):

    user = models.ForeignKey(
        User, related_name='sent_messages', verbose_name='المرسل', on_delete=models.CASCADE, db_index=True)
    receiver = models.ForeignKey(
        User, related_name='my_messages', verbose_name='المستقبل', on_delete=models.CASCADE)
    title = models.CharField(max_length=100, verbose_name='عنوان الرسالة', null=True, default=None)
    content = models.TextField(verbose_name='محتوى الرسالة', max_length=255)
    is_read = models.BooleanField(default=False, db_index=True)
    created = models.DateTimeField(
        auto_now_add=True, verbose_name='وقت اضافة الرسالة', db_index=True)
    updated = models.DateTimeField(
        auto_now=True, verbose_name='وقت تحديث الرسالة')

    class Meta:
        ordering = ('-created', )
        verbose_name = "رسالة"
        verbose_name_plural = "رسائل"

    def get_absolute_url(self):
        return reverse('raykomfi:get-message', args=[self.user.id, self.message.id])
    
    def get_noti_url(self):
        return reverse('raykomfi:get-message', args=[self.receiver.id, self.id])

    def __str__(self):
        return self.content
    
    def get_created_natural(self):
        return natural_time(self.created)

    def get_updated_natural(self):
        return natural_time(self.updated)

    
class Report(models.Model):
    user = models.ForeignKey(User, related_name='reported', on_delete=models.CASCADE, verbose_name='المبلغ')
    content = models.CharField(max_length=255)
    topic = models.CharField(max_length=255, default="")
    reported_url = models.CharField(max_length=255, default="")
    created = models.DateTimeField(auto_now_add=True, verbose_name='وقت اضافة الإبلاغ', db_index=True)
    resolved = models.BooleanField(default=False, verbose_name='تم المعالجة ؟')

    class Meta:
        ordering = ('-created',)
        verbose_name = "إبلاغ"
        verbose_name_plural = "إبلاغات"

    def __str__(self):
        return self.content

class NoRegistrationCode(models.Model):
    fakeUser = models.ForeignKey(User, related_name='fake_user', on_delete=models.SET_DEFAULT, default=None, null=True, blank=True)
    email = models.EmailField(unique=True, verbose_name='بريد الإلكتروني', null=True, blank=True)
    code = models.CharField(unique=True, max_length=150)
    accepted_conditions_terms = models.BooleanField(default=False)
    continent = models.CharField(max_length=155, default='')
    created = models.DateTimeField(auto_now_add=True, verbose_name='وقت اضافة الرمز', db_index=True)

    class Meta:
        ordering = ('-created',)
        verbose_name = "عضو بدون تسجيل"
        verbose_name_plural = "أعضاء بدون تسجيل"

    def __str__(self):
        return self.email

class ImportantAdminMessages(models.Model):
    message = models.TextField(blank=True, null=True)
    show = models.BooleanField(default=False)

    class Meta:
        verbose_name = "رسالة للزوار"
        verbose_name_plural = "رسائل للزوار"

class HomeAdMessages(models.Model):
    message = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "رسالة ترويجية"
        verbose_name_plural = "رسائل ترويجية"

class Hashtags(models.Model):
    hashtags = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "هاشتاق"
        verbose_name_plural = "هاشتاقات"
    
    def __str__(self):
        return 'هاشتاقات'