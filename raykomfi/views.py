from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.


def index(request):
    return render(request, 'sections/home.html')


def profile_view(request, id):
    return render(request, 'user/profile.html')


def sign_in_view(request):
    return render(request, 'user/signin.html')


def sign_up_view(request):
    return render(request, 'user/register.html')


def post_view(request, id):
    return render(request, 'sections/post_view.html')


def create_post(request):
    return render(request, 'sections/create_post.html')


def change_password_view(request):
    return render(request, 'user/change_password.html')


def forgot_password_view(request):
    return render(request, 'user/_password.html')
