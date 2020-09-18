from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Post, Comment, Message, Reply
from django_countries.fields import CountryField
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
from django import forms
from sorl.thumbnail import ImageField
from materializecssform.templatetags import materializecss


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

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)

        for fieldname in ['username', 'first_name', 'last_name', 'country', 'bio', 'email']:
            if fieldname == 'username':
                self.fields[fieldname].widget.attrs['placeholder'] = ''
                self.fields[fieldname].label = 'اسم المستخدم'
                self.fields[fieldname].widget.attrs['class'] = 'w3-input w3-border  w3-round'
            if fieldname == 'first_name':
                self.fields[fieldname].widget.attrs['placeholder'] = ''
                self.fields[fieldname].label = 'الاسم الاول'
                self.fields[fieldname].widget.attrs['class'] = 'w3-input w3-border  w3-round'
            if fieldname == 'last_name':
                self.fields[fieldname].widget.attrs['placeholder'] = ''
                self.fields[fieldname].label = 'الاسم الأخير'
                self.fields[fieldname].widget.attrs['class'] = 'w3-input w3-border  w3-round'
            if fieldname == 'country':
                self.fields[fieldname].widget.attrs['placeholder'] = ''
                self.fields[fieldname].label = 'الدولة'
                self.fields[fieldname].widget.attrs['class'] = 'w3-input w3-border  w3-round'
            if fieldname == 'email':
                self.fields[fieldname].widget.attrs['placeholder'] = ''
                self.fields[fieldname].label = 'الايميل'
                self.fields[fieldname].widget.attrs['class'] = 'w3-input w3-border  w3-round'
            if fieldname == 'bio':
                self.fields[fieldname].widget.attrs['placeholder'] = ''
                self.fields[fieldname].label = 'نبذة عنك'
                self.fields[fieldname].widget.attrs['class'] = 'w3-input w3-border  w3-round'


class ProfileForm(forms.Form):
    username = forms.CharField(label='', widget=forms.TextInput())
    first_name = forms.CharField(
        label='', required=False, widget=forms.TextInput())
    last_name = forms.CharField(
        label='', required=False, widget=forms.TextInput())
    country = forms.CharField(label='', required=False,
                              widget=forms.TextInput())
    bio = forms.CharField(label='', required=False,
                          max_length=144, widget=forms.Textarea())
    email = forms.CharField(label='', validators=[validate_email], widget=forms.TextInput(
        attrs={'placeholder': 'ايميل'}), error_messages={
        'unique': _("الايميل موجود مسبقا")
    })

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'country', 'bio', )

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)

        for fieldname in ['username', 'first_name', 'last_name', 'country', 'bio', 'email']:
            if fieldname == 'username':
                self.fields[fieldname].widget.attrs['placeholder'] = ''
                self.fields[fieldname].label = 'اسم المستخدم'
                self.fields[fieldname].widget.attrs['class'] = 'w3-input w3-border w3-round-large'
                self.fields[fieldname].widget.attrs.pop("autofocus", None)
            if fieldname == 'first_name':
                self.fields[fieldname].widget.attrs['placeholder'] = ''
                self.fields[fieldname].label = 'الاسم الاول'
                self.fields[fieldname].widget.attrs['class'] = 'w3-input w3-border  w3-round-large'
            if fieldname == 'last_name':
                self.fields[fieldname].widget.attrs['placeholder'] = ''
                self.fields[fieldname].label = 'الاسم الأخير'
                self.fields[fieldname].widget.attrs['class'] = 'w3-input w3-border  w3-round-large'
            if fieldname == 'country':
                self.fields[fieldname].widget.attrs['placeholder'] = ''
                self.fields[fieldname].label = 'الدولة'
                self.fields[fieldname].widget.attrs['class'] = 'w3-input w3-border  w3-round-large'
            if fieldname == 'email':
                self.fields[fieldname].widget.attrs['placeholder'] = ''
                self.fields[fieldname].label = 'الايميل'
                self.fields[fieldname].widget.attrs['class'] = 'w3-input w3-border  w3-round-large'
            if fieldname == 'bio':
                self.fields[fieldname].widget.attrs['placeholder'] = ''
                self.fields[fieldname].label = 'نبذة عنك'
                self.fields[fieldname].widget.attrs['class'] = 'w3-input w3-border  w3-round-large'


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


class NewPostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('category', 'title', 'content', 'image')

    def __init__(self, *args, **kwargs):
        super(NewPostForm, self).__init__(*args, **kwargs)

        for fieldname in ['category', 'title', 'content', 'image']:

            if fieldname == 'category':
                self.fields[fieldname].widget.attrs['placeholder'] = 'تصنيف الموضوع'
                self.fields[fieldname].label = ''
                self.fields[fieldname].empty_label = 'تصنيف الموضوع'
            if fieldname == 'title':
                self.fields[fieldname].widget.attrs['placeholder'] = 'عنوان الموضوع'
                self.fields[fieldname].label = ''
            if fieldname == 'content':
                self.fields[fieldname].widget.attrs['placeholder'] = 'نبذة عن الموضوع'
                self.fields[fieldname].label = ''
            if fieldname == 'image':
                self.fields[fieldname].widget.attrs['placeholder'] = 'صورة'

    def clean_image(self):
        image = self.cleaned_data.get('image')
        ALLOWED_EXT = ['jpg', 'png', 'jpeg']
        filesize = image.size
        extension = image.name.split('.')[1].lower()

        if filesize > 10485760:  # 10MB
            raise forms.ValidationError(
                "حجم الصورة يجب ان يكون اصغر من 10 ميغابايت")

        if extension not in ALLOWED_EXT:
            raise forms.ValidationError(
                "ملف الصورة تالف أو نوع الملف ليس صورة")

        return image


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


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('content',)

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)

        for fieldname in ['content']:

            if fieldname == 'content':
                self.fields[fieldname].widget.attrs['class'] = 'w3-input w3-border  w3-round-large'
                self.fields[fieldname].label = ''
                self.fields[fieldname].required = True


class ReplyForm(forms.ModelForm):

    class Meta:
        model = Reply
        fields = ('content',)

    def __init__(self, *args, **kwargs):
        super(ReplyForm, self).__init__(*args, **kwargs)

        for fieldname in ['content']:

            if fieldname == 'content':
                self.fields[fieldname].widget.attrs['rows'] = 1
                self.fields[fieldname].widget.attrs['class'] = 'w3-input w3-border  w3-round-large'
                self.fields[fieldname].label = ''
                self.fields[fieldname].required = True
