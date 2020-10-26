# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import AbstractUser
from django_countries.fields import CountryField
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django import forms
from sorl.thumbnail import ImageField
from cloudinary.models import CloudinaryField
from uuid import uuid4, uuid1

from django.core.cache import cache 
import datetime
from django.conf import settings
from django_countries.fields import CountryField

from hitcount.models import HitCountMixin, HitCount
from django.contrib.contenttypes.fields import GenericRelation


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


    def get_absolute_url(self):
        return reverse('raykomfi:user-profile', args=[self.id])

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
    image = ImageField(
        upload_to='post_images', verbose_name='صورة', default=None, null=True, blank=True)
    content = models.TextField(verbose_name='نبذة عن الموضوع', max_length=144, blank=True)
    isActive = models.BooleanField(default=True)
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

    def save(self, *args, **kwargs):
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
        ordering = ('created', )
        verbose_name = "تعليق"
        verbose_name_plural = "تعليقات"

    def __str__(self):
        return self.content

    def get_absolute_url(self):
        return reverse('raykomfi:post-view', args=[self.post.id, self.post.slug]) + f'#comment-id-{self.id}'

    def get_noti_url(self):
        return reverse('raykomfi:post-view', args=[self.post.id, self.post.slug]) + f'?read={self.id}' + f'#comment-id-{self.id}'


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
        return reverse('raykomfi:post-view', args=[self.comment.post.id, self.comment.post.slug]) + f'?read={self.id}' + f'#to-{self.id}'


class Message(models.Model):

    user = models.ForeignKey(
        User, related_name='sent_messages', verbose_name='المرسل', on_delete=models.CASCADE, db_index=True)
    receiver = models.ForeignKey(
        User, related_name='my_messages', verbose_name='المستقبل', on_delete=models.CASCADE)
    title = models.CharField(max_length=300, verbose_name='عنوان الرسالة', null=True, default=None)
    content = models.TextField(verbose_name='محتوى الرسالة')
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