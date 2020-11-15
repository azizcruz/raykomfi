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
import datetime
from django.conf import settings
from django_countries.fields import CountryField

from hitcount.models import HitCountMixin, HitCount
from django.contrib.contenttypes.fields import GenericRelation
from tinymce.models import HTMLField
from notifications.signals import notify
from twitter import *
from dotenv import load_dotenv
load_dotenv()
import os
import pytz

utc=pytz.UTC

BASE_URL = 'https://raykomfi.com' if os.getenv('environment') == 'prod' else 'http://localhost:8000'




def slugify(str):
    str = str.replace(" ", "-")
    str = str.replace(",", "-")
    str = str.replace("(", "-")
    str = str.replace(")", "")
    str = str.replace("؟", "")
    return str


class User(AbstractUser):
    bio = models.TextField(blank=True, verbose_name='نبذة عن',)
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


    def get_absolute_url(self):
        return reverse('raykomfi:user-profile', args=[self.id])

    def online(self):
        if self.last_login:
            now = datetime.datetime.now()
            last_seen = cache.get(f'seen_{self.username}')
            if not last_seen:
                return False

            if last_seen.replace(microsecond = 0).replace(tzinfo=None) == now.replace(microsecond = 0):
                return True
            else:
                return False
        else:
            return False 

class Category(models.Model):

    name = models.CharField(
        max_length=200, verbose_name='اسم التصنيف', db_index=True)
    slug = models.CharField(
        max_length=200, db_index=True, unique=True, blank=True)

    class Meta:
        ordering = ("name", )
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
    creator = models.ForeignKey(
        User, related_name='posts', verbose_name='الكاتب',  on_delete=models.SET_DEFAULT, default=None, null=True, db_index=True)
    category = models.ForeignKey(
        Category, verbose_name='التصنيف', null=True, on_delete=models.SET_DEFAULT, default=None, db_index=True)
    title = models.CharField(
        max_length=200, verbose_name='الموضوع', db_index=True)
    slug = models.CharField(
        max_length=200, db_index=True, null=True, blank=True)
    image_url = models.CharField(verbose_name='رابط الصورة', blank=True, null=True, max_length=1000)
    image_source = models.CharField(verbose_name='مصدر الصورة', blank=True, null=True, max_length=1000)
    content = models.TextField(verbose_name='نبذة عن الموضوع', max_length=144, blank=True, db_index=True)
    isActive = models.BooleanField(default=False, db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    hit_count_generic = GenericRelation(HitCount, object_id_field='object_pk', related_query_name='hit_count_generic_relation')

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


    def save(self, *args, **kwargs):
        # When post gets accepted
        prev_post_status = Post.objects.filter(pk=self.pk)
        if len(prev_post_status) > 0:
            if prev_post_status != self.isActive and self.isActive == True:
                # Post to twitter
                t = Twitter(auth=OAuth(os.getenv('access_token'), os.getenv('access_token_secret'), os.getenv('consumer_key'), os.getenv('consumer_secret')))
                t.statuses.update(status=self.get_twitter_url(), media_ids="")

                prev_post_status = prev_post_status.values('isActive').first()['isActive']
                admin = User.objects.get(email=os.getenv('ADMIN_EMAIL'))
                notify.send(admin, recipient=self.creator ,action_object=self, description=self.get_noti_url(), target=self, verb='post_accepted')
        # Generate slug
        self.slug = slugify(self.title)
        super(Post, self).save(*args, **kwargs)

class Comment(models.Model):

    user = models.ForeignKey(
        User, related_name='my_comments', verbose_name='صاحب النعليق', on_delete=models.SET_DEFAULT, default=None, null=True, db_index=True)
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
        return reverse('raykomfi:post-view', args=[self.post.id, self.post.slug]) + f'?all_comments=true' + f'#comment-id-{self.id}'



class Reply(models.Model):

    user = models.ForeignKey(
        User, related_name='my_replies', verbose_name='صاحب النعليق', on_delete=models.SET_DEFAULT, default=None, null=True, db_index=True)
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
        return reverse('raykomfi:post-view', args=[self.comment.post.id, self.comment.post.slug])+ f'?all_comments=true' + f'?read={self.id}' + f'#to-{self.id}'


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
        return reverse('raykomfi:get-message', args=[self.user.id, self.id]) + f'?read={self.id}' + f'#to-{self.id}'

    def __str__(self):
        return self.content

    
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