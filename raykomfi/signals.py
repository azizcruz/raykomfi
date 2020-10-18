from django.db.models.signals import post_save
from notifications.signals import notify
from raykomfi.models import Reply, Comment, Message

def new_reply(sender, instance, created, **kwargs):
    notify.send(instance, verb='was saved')

def new_comment(sender, instance, created, **kwargs):
    notify.send(instance, verb='was saved')

def new_message(sender, instance, created, **kwargs):
    notify.send(instance, verb='was saved')


post_save.connect(new_reply, sender=Reply)
post_save.connect(new_comment, sender=Comment)
post_save.connect(new_message, sender=Message)