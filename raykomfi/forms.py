from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Post
from django_countries.fields import CountryField
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm
from django.utils.translation import gettext_lazy as _


class SignupForm(UserCreationForm):
    username = forms.CharField(label='', widget=forms.TextInput(
        attrs={'placeholder': 'اسم المستخدم'}))
    first_name = forms.CharField(label='', required=False, widget=forms.TextInput(
        attrs={'placeholder': 'الاسم الاول'}))
    last_name = forms.CharField(label='', required=False, widget=forms.TextInput(
        attrs={'placeholder': 'الاسم الاخير'}))
    country = forms.CharField(label='', required=False, widget=forms.TextInput(
        attrs={'placeholder': 'الدولة'}))
    bio = forms.CharField(label='', required=False, max_length=144, help_text='مسموح فقط 144 حرف', widget=forms.Textarea(
        attrs={'placeholder': 'نبذة عنك'}))
    email = forms.CharField(label='', validators=[validate_email], widget=forms.TextInput(
        attrs={'placeholder': 'ايميل'}), error_messages={
        'unique': _("الايميل موجود مسبقا")
    })
    password1 = forms.CharField(label='', widget=forms.PasswordInput(
        {'placeholder': 'كلمة المرور'}))
    password2 = forms.CharField(label='', widget=forms.PasswordInput(
        {'placeholder': 'تأكيد كلمة المرور'}))

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2',
                  'email', 'first_name', 'last_name', 'country', 'bio', )


class SigninForm(forms.Form):
    username = forms.CharField(label='', widget=forms.TextInput(
        attrs={'placeholder': 'اسم المستخدم'}))
    password = forms.CharField(label='', widget=forms.PasswordInput(
        {'placeholder': 'كلمة المرور'}))

    class Meta:
        model = User
        fields = ('username', 'password',)


class CustomPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super(CustomPasswordResetForm, self).__init__(*args, **kwargs)

        for fieldname in ['email']:

            if fieldname == 'email':
                self.fields[fieldname].widget.attrs['placeholder'] = 'بريد الكتروني'
                self.fields[fieldname].label = ''


class NewPostForm(forms.Form):

    class Meta:
        model = Post
        fields = ('category', 'title', 'content', 'image')


class CustomChangePasswordForm(PasswordChangeForm):

    def __init__(self, *args, **kwargs):
        super(CustomChangePasswordForm, self).__init__(*args, **kwargs)

        for fieldname in ['old_password', 'new_password1', 'new_password2']:

            if fieldname == 'old_password':
                self.fields[fieldname].widget.attrs['placeholder'] = 'كلمة المرور الحالية'
                self.fields[fieldname].label = ''
            if fieldname == 'new_password1':
                self.fields[fieldname].widget.attrs['placeholder'] = 'كلمة المرور الجديدة'
                self.fields[fieldname].label = ''
            if fieldname == 'new_password2':
                self.fields[fieldname].widget.attrs['placeholder'] = 'تأكيد كلمة الجديدة'
                self.fields[fieldname].label = ''
