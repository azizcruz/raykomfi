from django.test import TestCase
from raykomfi.models import User, Post, Message, Comment, Reply
from django.shortcuts import reverse

class RaykomfiTestCase(TestCase):
    def setUp(self):
        # create activated user
        # url = reverse('raykomfi:register')
        # data = {}
        # resp = self.client.post(url, data)
        pass

    def fetch_messages(self):
        pass