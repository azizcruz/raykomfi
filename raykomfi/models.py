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

def slugify(str):
    str = str.replace(" ", "-")
    str = str.replace(",", "-")
    str = str.replace("(", "-")
    str = str.replace(")", "")
    str = str.replace("؟", "")
    return str


class User(AbstractUser):
    bio = models.TextField(blank=True, verbose_name='نبذة عن',)
    country = models.CharField(max_length=255, verbose_name='الدولة',)
    isBlocked = models.BooleanField(default=False, verbose_name='محظور؟')
    uuid = models.UUIDField(default=uuid4, editable=False, verbose_name='رمز العضو', null=True)
    secret_code = models.UUIDField(default=uuid1, editable=False, verbose_name='رمز العمليات', null=True)
    email_active = models.BooleanField(
        default=False, verbose_name='ايميل مفعل')
    stay_logged_in = models.BooleanField(
        default=False, verbose_name='البقاء متصلا')
    email = models.EmailField(unique=True, verbose_name='بريد الإلكتروني',)


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


class Post(models.Model):
    creator = models.ForeignKey(
        User, related_name='posts', verbose_name='الكاتب',  on_delete=models.SET_DEFAULT, default=None, null=True)
    category = models.ForeignKey(
        Category, verbose_name='التصنيف', null=True, on_delete=models.SET_DEFAULT, default=None)
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
        User, related_name='my_comments', verbose_name='صاحب النعليق', on_delete=models.SET_DEFAULT, default=None, null=True)
    post = models.ForeignKey(
        Post, related_name='comments', verbose_name='المنشور', on_delete=models.CASCADE)
    content = models.TextField(verbose_name='التعليق')
    isActive = models.BooleanField(default=True, verbose_name='مفعل؟')
    votes = models.IntegerField(default=0)
    voted_like = models.ManyToManyField(
        User, related_name='comment_likes', verbose_name='الاعضاء المتفقين')
    voted_dislike = models.ManyToManyField(
        User, related_name='comment_dislikes', verbose_name='الاعضاء الغير متفقين')
    created = models.DateTimeField(
        auto_now_add=True, verbose_name='وقت اضافة التعليق')
    updated = models.DateTimeField(
        auto_now=True, verbose_name='وقت تحديث التعليق')

    class Meta:
        ordering = ('created', )
        verbose_name = "تعليق"
        verbose_name_plural = "تعليقات"

    def __str__(self):
        return self.content


class Reply(models.Model):

    user = models.ForeignKey(
        User, related_name='my_replies', verbose_name='صاحب النعليق', on_delete=models.SET_DEFAULT, default=None, null=True)
    comment = models.ForeignKey(
        Comment, related_name='replies', verbose_name='التعليق', on_delete=models.CASCADE)
    content = models.TextField()
    isActive = models.BooleanField(default=True, verbose_name='مفعل؟')
    created = models.DateTimeField(
        auto_now_add=True, verbose_name='وقت اضافة التعليق')
    updated = models.DateTimeField(
        auto_now=True, verbose_name='وقت تحديث التعليق')

    class Meta:
        ordering = ('created', )
        verbose_name = "رد على تعليق"
        verbose_name_plural = "ردود على التعليقات"

    def __str__(self):
        return self.content


class Message(models.Model):

    user = models.ForeignKey(
        User, related_name='sent_messages', verbose_name='صاحب النعليق', on_delete=models.CASCADE)
    receiver = models.ForeignKey(
        User, related_name='my_messages', verbose_name='المستقبل', on_delete=models.CASCADE)
    title = models.CharField(max_length=300, verbose_name='عنوان الرسالة', null=True, default=None)
    content = models.TextField(verbose_name='محتوى الرسالة')
    is_read = models.BooleanField(default=False)
    created = models.DateTimeField(
        auto_now_add=True, verbose_name='وقت اضافة الرسالة')
    updated = models.DateTimeField(
        auto_now=True, verbose_name='وقت تحديث الرسالة')

    class Meta:
        ordering = ('-created', )
        verbose_name = "رسالة"
        verbose_name_plural = "رسائل"

    def __str__(self):
        return self.content