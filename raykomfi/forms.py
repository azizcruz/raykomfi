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


def custom_render(element, markup_classes):
    element_type = element.__class__.__name__.lower()

    # Get the icon set setting
    icon_set = materializecss.config.MATERIALIZECSS_ICON_SET

    if element_type == 'boundfield':
        materializecss.add_input_classes(element)
        template = materializecss.get_template(
            "materialcss_override/field.html")
        context = {'field': element,
                   'classes': markup_classes, 'icon_set': icon_set}
    else:
        has_management = getattr(element, 'management_form', None)
        if has_management:
            for form in element.forms:
                for field in form.visible_fields():
                    materializecss.add_input_classes(field)

            template = materializecss.get_template(
                "materializecssform/formset.html")
            context = {'formset': element,
                       'classes': markup_classes, 'icon_set': icon_set}
        else:
            for field in element.visible_fields():
                materializecss.add_input_classes(field)

            template = materializecss.get_template(
                "materializecssform/form.html")
            context = {'form': element,
                       'classes': markup_classes, 'icon_set': icon_set}

    return template.render(context)


materializecss.render = custom_render


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
                self.fields[fieldname].widget.attrs['placeholder'] = 'اكتب تعليق'
                self.fields[fieldname].label = ''
                self.fields[fieldname].required = True
