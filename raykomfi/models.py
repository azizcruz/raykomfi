# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import AbstractUser
from django_countries.fields import CountryField
from django.urls import reverse


def slugify(str):
    str = str.replace(" ", "-")
    str = str.replace(",", "-")
    str = str.replace("(", "-")
    str = str.replace(")", "")
    str = str.replace("؟", "")
    return str


class User(AbstractUser):
    bio = models.TextField(max_length=500, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    country = CountryField()
    isBlocked = models.BooleanField(default=False)


class Category(models.Model):

    name = models.CharField(max_length=200, db_index=True)
    slug = models.CharField(
        max_length=200, db_index=True, unique=True, blank=True)

    class Meta:
        ordering = ("name", )
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('raykomfi:list_post_category', args=[self.slug])

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)


class Post(models.Model):

    category = models.ForeignKey(
        Category, related_name='posts', null=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=200, db_index=True)
    slug = models.CharField(
        max_length=200, db_index=True, null=True, blank=True)
    Image = models.ImageField(
        upload_to='post_images', default='post_images/default.png')
    content = models.TextField()
    isActive = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created', )
        index_together = (('id', 'slug'), )
        verbose_name = "Post"
        verbose_name_plural = "Posts"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('raykomfi:post_detail', args=[self.id, self.slug])

    def get_image_url(self):
        return self.Image.url

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Post, self).save(*args, **kwargs)


class Comment(models.Model):

    user = models.ForeignKey(
        User, related_name='comments', on_delete=models.SET('مجهول'))
    post = models.ForeignKey(
        Post, related_name='comments', on_delete=models.CASCADE)
    content = models.TextField()
    isActive = models.BooleanField(default=True)
    likes = models.ManyToManyField(User, related_name='likes')
    dislikes = models.ManyToManyField(User, related_name='dislikes')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created', )
        verbose_name = "Comment"
        verbose_name_plural = "Comments"

    def __str__(self):
        return self.content


class Reply(models.Model):

    user = models.ForeignKey(
        User, related_name='replies', on_delete=models.SET('مجهول'))
    comment = models.ForeignKey(
        Comment, related_name='replies', on_delete=models.CASCADE)
    content = models.TextField()
    isActive = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created', )
        verbose_name = "Reply"
        verbose_name_plural = "Replies"

    def __str__(self):
        return self.content


class Message(models.Model):

    sender = models.ForeignKey(
        User, related_name='sent_messages', on_delete=models.SET('مجهول'))
    receiver = models.ForeignKey(
        User, related_name='mymessages', on_delete=models.CASCADE)
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created', )
        verbose_name = "Message"
        verbose_name_plural = "Messages"

    def __str__(self):
        return self.content
