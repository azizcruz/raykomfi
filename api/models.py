from django.db import models

# Create your models here.
class BestUserListTrack(models.Model):
    content = models.TextField(verbose_name='الترتيب')
    created = models.DateTimeField(
        auto_now_add=True, verbose_name='تاريخ التحديد', db_index=True)
    updated = models.DateTimeField(
        auto_now=True, verbose_name='تاريخ التحديث')

    class Meta:
        ordering = ('-created',)
        verbose_name = "ترتيب الاعضاء"
        verbose_name_plural = "الترتيب"


class Hashtags(models.Model):
    hashtags = models.TextField(blank=True, null=True)