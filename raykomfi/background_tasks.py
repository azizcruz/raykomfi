from django.utils.functional import SimpleLazyObject
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
from notifications.signals import notify
from .models import User, Message, Post, Comment, Reply, Report

def send_email(html_email_template, mail_subject, to_email, from_email, token):
    msg = EmailMultiAlternatives(
        f"{mail_subject}", "nothing", from_email, [to_email])
    msg.attach_alternative(html_email_template, "text/html")
    msg.send()

def send_notify(notify_model, sender_id, recipient_id , action_object_id, target, verb, description=None):
    sender = User.objects.filter(id=sender_id)
    receiver = User.objects.filter(id=recipient_id)
    action_object = ''
    if notify_model == 'comment':
        action_object = Comment.objects.filter(id=action_object_id).first()
        description = action_object.get_noti_url()
        target = action_object

    if notify_model == 'post':
        action_object = Post.objects.filter(id=action_object_id).first()
        description = action_object.get_absolute_url()
        target = action_object
    if notify_model == 'reply':
        action_object = Reply.objects.filter(id=action_object_id).first()
        description = action_object.get_noti_url()
        target = action_object.comment
    if notify_model == 'message':
        action_object = Comment.objects.filter(id=action_object_id).first()
        description = action_object.get_noti_url()
        target = action_object
    if notify_model == 'report':
        action_object = Report.objects.filter(id=action_object_id).first()
        target = action_object

    notify.send(sender, recipient=receiver, action_object=action_object,  description=description, target=action_object, verb=verb)
