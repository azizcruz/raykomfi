from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Post, Comment, Message, Reply
from django_countries.fields import CountryField
from django.core.exceptions import ValidationError
from django.core.validators import validate_email, MinLengthValidator, MaxLengthValidator
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
from django import forms
from sorl.thumbnail import ImageField
from django.contrib.auth import password_validation
from parsley.decorators import parsleyfy
from django.core.validators import RegexValidator

# username_validator = RegexValidator(r"^(?=.*[a-zA-Z0-9])\w{6,}$", "إسم المستخدم يجب أن يكون على الأقل 6 أحرف و باللغة الإنجليزية")
username_validator = RegexValidator(r"^.{6,15}$", "إسم المستخدم يجب أن يكون على الأقل 6 أحرف")


@parsleyfy
class SignupForm(UserCreationForm):
    username = forms.CharField(validators=[MinLengthValidator(6), MaxLengthValidator(30), username_validator])
    first_name = forms.CharField(required=False, widget=forms.TextInput())
    last_name = forms.CharField(required=False, widget=forms.TextInput())
    country = forms.CharField(required=False,
                              widget=forms.HiddenInput())
    bio = forms.CharField(required=False, max_length=144,
                          widget=forms.Textarea())
    email = forms.EmailField(label='', validators=[validate_email], widget=forms.TextInput(), error_messages={
        'unique': _("البريد الإلكتروني موجود مسبقا"),
        'invalid': _("بريد إلكتروني غير صالح"),

    })
    password1 = forms.CharField(label='', widget=forms.PasswordInput())
    password2 = forms.CharField(label='', widget=forms.PasswordInput(), error_messages={
        'password_mismatch': _("كلمات المرور غير متطابقة"),

    })

    class Meta:
        model = User
        parsley_extras = {
            'username': {
                # 'pattern': '^(?=.*[a-zA-Z0-9])\w{6,}$',
                'pattern': '^.{6,15}$',
                # 'pattern-message': 'إسم المستخدم يجب أن يكون على الأقل 6 أحرف و باللغة الإنجليزية',
                'pattern-message': 'إسم المستخدم يجب أن يكون بين 6 و 15 حرف',
            },
            'password1': {
                'pattern': '^(?=.*[a-zA-Z])(?=\w*[0-9])\w{8,}$',
                'pattern-message': 'كلمة المرور يجب أن تكون على الأقل 8 أحرف وأرقام و بالأحرف الاتينية',
            },
            'password2': {
                'equalto': "password1",
                'equalto-message': "كلمات المرور غير متطابقة",
            },
             'bio': {
                'maxlength-message': "تعديت الحد المسموح",
            },
        }
        fields = ('username', 'password1', 'password2',
                  'email', 'first_name', 'last_name', 'country', 'bio', )

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)

        for fieldname in ['username', 'first_name', 'last_name', 'country', 'bio', 'email', 'password1', 'password2']:
            if fieldname == 'username':
                self.fields[fieldname].widget.attrs['placeholder'] = ''
                self.fields[fieldname].label = 'اسم المستخدم'
                self.fields[fieldname].widget.attrs['class'] = 'w3-input w3-border  '
                self.fields[fieldname].widget.attrs.pop("autofocus", None)
            if fieldname == 'first_name':
                self.fields[fieldname].widget.attrs['placeholder'] = ''
                self.fields[fieldname].label = 'الاسم الاول'
                self.fields[fieldname].widget.attrs['class'] = 'w3-input w3-border  '
            if fieldname == 'last_name':
                self.fields[fieldname].widget.attrs['placeholder'] = ''
                self.fields[fieldname].label = 'الاسم الأخير'
                self.fields[fieldname].widget.attrs['class'] = 'w3-input w3-border  '
            if fieldname == 'country':
                self.fields[fieldname].widget.attrs['placeholder'] = ''
                self.fields[fieldname].label = 'الدولة'
                self.fields[fieldname].widget.attrs['class'] = 'w3-input w3-border  '
            if fieldname == 'email':
                self.fields[fieldname].widget.attrs['placeholder'] = ''
                self.fields[fieldname].label = 'الايميل'
                self.fields[fieldname].widget.attrs['class'] = 'w3-input w3-border  '
            if fieldname == 'bio':
                self.fields[fieldname].widget.attrs['placeholder'] = 'مسموح فقط 144 حرف'
                self.fields[fieldname].label = 'نبذة عنك'
                self.fields[fieldname].widget.attrs['class'] = 'w3-input w3-border  '
            if fieldname == 'password1':
                self.fields[fieldname].widget.attrs['placeholder'] = ''
                self.fields[fieldname].label = 'كلمة المرور'
                self.fields[fieldname].widget.attrs['class'] = 'w3-input w3-border  '
                self.fields[fieldname].help_text = '<ul><li>كلمة المرور لا يمكن أن تكون مشابهة للمعلومات الشخصية الأخرى.</li><li>كلمة المرور الخاصة بك يجب أن تتضمن 8 حروف على الأقل.</li><li>كلمة المرور لا يمكن أن تكون سهلة شائعة الاستخدام.</li><li>كلمة المرور لا يمكن أن تحتوي على أرقام فقط.</li></ul>'
            if fieldname == 'password2':
                self.fields[fieldname].widget.attrs['placeholder'] = ''
                self.fields[fieldname].label = 'تأكيد كلمة المرور'
                self.fields[fieldname].widget.attrs['class'] = 'w3-input w3-border  '

@parsleyfy
class ProfileForm(forms.ModelForm):
    username = forms.CharField(validators=[MinLengthValidator(6), MaxLengthValidator(15), username_validator])
    first_name = forms.CharField(
        label='', required=False, widget=forms.TextInput())
    last_name = forms.CharField(
        label='', required=False, widget=forms.TextInput())
    bio = forms.CharField(label='', required=False,
                          max_length=144, widget=forms.Textarea())
    email = forms.EmailField(label='', validators=[validate_email], widget=forms.TextInput(), error_messages={
        'unique': _("البريد الإلكتروني موجود مسبقا"),
        'invalid': _("بريد إلكتروني غير صالح"),
    })


    class Meta:
        model = User
        parsley_extras = {
            'username': {
                # 'pattern': '^(?=.*[a-zA-Z0-9])\w{6,}$',
                'pattern': '^.{6,15}$',
                # 'pattern-message': 'إسم المستخدم يجب أن يكون على الأقل 6 أحرف و باللغة الإنجليزية',
                'pattern-message': 'إسم المستخدم يجب أن يكون بين 6 و 15 حرف',
            },
            'bio': {
                'maxlength-message': "تعديت الحد المسموح",
            },
        }
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'stay_logged_in', 'get_notifications', 'hide_name', 'allow_messages')

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)

        for fieldname in ['username', 'first_name', 'last_name', 'bio', 'email', 'stay_logged_in', 'get_notifications', 'hide_name', 'allow_messages']:
            if fieldname == 'username':
                self.fields[fieldname].widget.attrs['placeholder'] = ''
                self.fields[fieldname].label = 'اسم المستخدم'
                self.fields[fieldname].widget.attrs['class'] = 'w3-input w3-border '
                self.fields[fieldname].widget.attrs.pop("autofocus", None)
            if fieldname == 'first_name':
                self.fields[fieldname].widget.attrs['placeholder'] = ''
                self.fields[fieldname].label = 'الاسم الاول'
                self.fields[fieldname].widget.attrs['class'] = 'w3-input w3-border  '
            if fieldname == 'last_name':
                self.fields[fieldname].widget.attrs['placeholder'] = ''
                self.fields[fieldname].label = 'الاسم الأخير'
                self.fields[fieldname].widget.attrs['class'] = 'w3-input w3-border  '
            if fieldname == 'email':
                self.fields[fieldname].widget.attrs['placeholder'] = ''
                self.fields[fieldname].label = 'الايميل'
                self.fields[fieldname].widget.attrs['class'] = 'w3-input w3-border  '
            if fieldname == 'bio':
                self.fields[fieldname].widget.attrs['placeholder'] = ''
                self.fields[fieldname].label = 'نبذة عنك'
                self.fields[fieldname].widget.attrs['class'] = 'w3-input w3-border  '
            if fieldname == 'stay_logged_in':
                self.fields[fieldname].widget.attrs['placeholder'] = ''
                self.fields[fieldname].label = 'البقاء متصلا ً'
                self.fields[fieldname].widget.attrs['class'] = 'raykomfi-input'
            if fieldname == 'get_notifications':
                self.fields[fieldname].widget.attrs['placeholder'] = ''
                self.fields[fieldname].label = 'السماح بالإشعارات'
                self.fields[fieldname].widget.attrs['class'] = 'raykomfi-input'
            if fieldname == 'hide_name':
                self.fields[fieldname].widget.attrs['placeholder'] = ''
                self.fields[fieldname].label = 'إخفاء الإسم الشخصي'
                self.fields[fieldname].widget.attrs['class'] = 'raykomfi-input'
            if fieldname == 'allow_messages':
                self.fields[fieldname].widget.attrs['placeholder'] = ''
                self.fields[fieldname].label = 'السماح بالرسائل الخاصة'
                self.fields[fieldname].widget.attrs['class'] = 'raykomfi-input'

@parsleyfy
class SigninForm(forms.Form):
    email = forms.EmailField(label='', validators=[validate_email], widget=forms.TextInput(), error_messages={
        'invalid': _("بريد إلكتروني غير صالح"),
    })
    password = forms.CharField(widget=forms.PasswordInput())
    stay_logged_in = forms.CharField(widget=forms.CheckboxInput())

    class Meta:
        model = User
        parsley_extras = {
            'stay_logged_in': {
                'required': 'false',
            },
        }
        fields = ('email', 'password',)

    def __init__(self, *args, **kwargs):
        super(SigninForm, self).__init__(*args, **kwargs)

        for fieldname in ['email', 'password', 'stay_logged_in']:
            if fieldname == 'email':
                self.fields[fieldname].widget.attrs['placeholder'] = ''
                self.fields[fieldname].label = 'البريد الإلكتروني'
                self.fields[fieldname].widget.attrs['class'] = 'w3-input w3-border  '
            if fieldname == 'password':
                self.fields[fieldname].widget.attrs['placeholder'] = ''
                self.fields[fieldname].label = 'كلمة المرور'
                self.fields[fieldname].widget.attrs['class'] = 'w3-input w3-border  '
            if fieldname == 'stay_logged_in':
                self.fields[fieldname].widget.attrs['placeholder'] = ''
                self.fields[fieldname].label = 'البقاء متصلا'
                self.fields[fieldname].widget.attrs['class'] = 'w3-check raykomfi-margin-small w3-border'


@parsleyfy
class ChangeEmailForm(forms.Form):
    current_email = forms.EmailField(label='', validators=[validate_email], widget=forms.TextInput(), error_messages={
        'invalid': _("بريد إلكتروني غير صالح"),
    })
    new_email1 = forms.EmailField(label='', validators=[validate_email], widget=forms.TextInput(), error_messages={
        'unique': _("البريد الإلكتروني موجود مسبقا"),
        'invalid': _("بريد إلكتروني غير صالح"),
    })
    new_email2 = forms.EmailField(label='', validators=[validate_email], widget=forms.TextInput(), error_messages={
        'unique': _("البريد الإلكتروني موجود مسبقا"),
        'invalid': _("بريد إلكتروني غير صالح"),
    })

    class Meta:
        parsley_extras = {
            'new_email2': {
                'equalto': "new_email1",
                'equalto-message': "بريد إلكتروني غير متطابق",
            }
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(ChangeEmailForm, self).__init__(*args, **kwargs)

        for fieldname in ['current_email', 'new_email1', 'new_email2']:
            if fieldname == 'current_email':
                self.fields[fieldname].widget.attrs['placeholder'] = ''
                self.fields[fieldname].widget.attrs['class'] = 'w3-input w3-border  '
                self.fields[fieldname].label = 'البريد الإلكتروني الحالي'

            if fieldname == 'new_email1':
                self.fields[fieldname].widget.attrs['placeholder'] = ''
                self.fields[fieldname].widget.attrs['class'] = 'w3-input w3-border  '
                self.fields[fieldname].label = 'البريد الإلكتروني الجديد'

            if fieldname == 'new_email2':
                self.fields[fieldname].widget.attrs['placeholder'] = ''
                self.fields[fieldname].widget.attrs['class'] = 'w3-input w3-border  '
                self.fields[fieldname].label = 'تكرار البريد الإلكتروني الجديد'

    def clean_current_email(self, *args, **kwargs):
        current_email = self.cleaned_data.get('current_email')

        if self.request.user.email != current_email:
            raise forms.ValidationError(
                    "بريدك الإلكتروني الحالي غير صحيح")

        return current_email

    def clean_new_email1(self, *args, **kwargs):
        new_email1 = self.cleaned_data.get('new_email1')

        
        if User.objects.filter(email=new_email1).exists():
            raise forms.ValidationError(
                    "البريد الإلكتروني موجود مسبقا")

        return new_email1

    def clean_new_email2(self, *args, **kwargs):
        new_email2 = self.cleaned_data.get('new_email2')

        
        if User.objects.filter(email=new_email2).exists():
            raise forms.ValidationError(
                    "البريد الإلكتروني موجود مسبقا")

        return new_email2




@parsleyfy
class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(label='', validators=[validate_email], widget=forms.TextInput(), error_messages={
        'invalid': _("بريد إلكتروني غير صالح"),
    })

    def __init__(self, *args, **kwargs):
        super(CustomPasswordResetForm, self).__init__(*args, **kwargs)

        for fieldname in ['email']:
            if fieldname == 'email':
                self.fields[fieldname].widget.attrs['placeholder'] = ''
                self.fields[fieldname].widget.attrs['class'] = 'w3-input w3-border  '
                self.fields[fieldname].label = 'بريد إلكتروني'

@parsleyfy
class NewPostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('category', 'title', 'content', 'image_url', 'image_source')

    def __init__(self, *args, **kwargs):
        super(NewPostForm, self).__init__(*args, **kwargs)

        for fieldname in ['category', 'title', 'content', 'image', 'image_url', 'image_source']:

            if fieldname == 'category':
                self.fields[fieldname].label = '* تصنيف الإستفسار'
                self.fields[fieldname].widget.attrs['class'] = 'w3-select w3-border  '
            if fieldname == 'title':
                self.fields[fieldname].label = '* عنوان الإستفسار'
                self.fields[fieldname].widget.attrs['class'] = 'w3-input w3-border  '
            if fieldname == 'content':
                self.fields[fieldname].widget.attrs['class'] = 'w3-input w3-border  '
                self.fields[fieldname].label = ' نبذة عن الإستفسار'
            if fieldname == 'image_url':
                self.fields[fieldname].label = 'رابط صورة '
                self.fields[fieldname].widget.attrs['class'] = 'w3-input w3-border  '
            if fieldname == 'image_source':
                self.fields[fieldname].label = 'مصدر الصورة (رابط الموقع الذي تعرض عليه الصورة)'
                self.fields[fieldname].widget.attrs['class'] = 'w3-input w3-border  '

    def clean_image_source(self):
        image_url = self.cleaned_data.get('image_url')
        image_source = self.cleaned_data.get('image_source')
        if image_source and not image_source:
            raise forms.ValidationError(
                "مصدر الصورة يجب أن لا يكون فارغا")

        return image_source

    def clean_title(self):
        title = self.cleaned_data.get('title')
        ALLOWED_EXT = ['jpg', 'png', 'jpeg']
        if title.find('رايكم في') == -1:
            raise forms.ValidationError(
                    "يجب أن يبدأ عنوان الإستفسار بعبارة رايكم في")

        if len(title) - 15 < 0 :
            raise forms.ValidationError(
                    "إستفسر عن شيء حقيقي")

        return title

@parsleyfy
class CustomChangePasswordForm(PasswordChangeForm):

    class Meta:

        parsley_extras = {
                'new_password1': {
                    'pattern': '^(?=.*[a-zA-Z])(?=\w*[0-9])\w{8,}$',
                    'pattern-message': 'كلمة المرور يجب أن تكون على الأقل 8 أحرف وأرقام و بالأحرف الاتينية',
                },
                'new_password2': {
                    'equalto': "new_password1",
                    'equalto-message': "كلمات المرور غير متطابقة",
                },
            }   

    def __init__(self, *args, **kwargs):
        super(CustomChangePasswordForm, self).__init__(*args, **kwargs)

        for fieldname in ['old_password', 'new_password1', 'new_password2']:

            if fieldname == 'old_password':
                self.fields[fieldname].widget.attrs['placeholder'] = ''
                self.fields[fieldname].widget.attrs['class'] = 'w3-input w3-border  '
                self.fields[fieldname].label = 'كلمة المرور الحالية'
            if fieldname == 'new_password1':
                self.fields[fieldname].widget.attrs['placeholder'] = ''
                self.fields[fieldname].widget.attrs['class'] = 'w3-input w3-border  '
                self.fields[fieldname].label = 'كلمة المرور الجديدة'
            if fieldname == 'new_password2':
                self.fields[fieldname].widget.attrs['placeholder'] = ''
                self.fields[fieldname].widget.attrs['class'] = 'w3-input w3-border  '
                self.fields[fieldname].label = 'تأكيد كلمة الجديدة'

class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('content',)

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)

        for fieldname in ['content']:

            if fieldname == 'content':
                self.fields[fieldname].widget.attrs['rows'] = 3
                self.fields[fieldname].widget.attrs['class'] = 'w3-input w3-border  '
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
                self.fields[fieldname].widget.attrs['rows'] = 2
                self.fields[fieldname].widget.attrs['class'] = 'w3-input w3-border  '
                self.fields[fieldname].label = ''
                self.fields[fieldname].required = True

@parsleyfy
class MessageForm(forms.ModelForm):

    class Meta:
        parsley_extras = {
                'content': {
                    'maxlength': 255,
                    'maxlength-message': "لقد تعديت الحد المسموح",
                },
            }  
        model = Message
        fields = ('title', 'content')

    def __init__(self, *args, **kwargs):
        super(MessageForm, self).__init__(*args, **kwargs)

        for fieldname in ['title','content']:
            if fieldname == 'title':
                self.fields[fieldname].widget.attrs['class'] = 'w3-input w3-border  '
                self.fields[fieldname].widget.attrs['placeholder'] = ''
                self.fields[fieldname].required = True
            if fieldname == 'content':
                self.fields[fieldname].widget.attrs['rows'] = 10
                self.fields[fieldname].widget.attrs['class'] = 'w3-input w3-border  '
                self.fields[fieldname].widget.attrs['placeholder'] = ''
                self.fields[fieldname].widget.attrs['id'] = 'new-message-content'
                self.fields[fieldname].help_text = 'مسموح 255 حرف فقط'

@parsleyfy
class RestorePasswordForm(forms.Form):
    password1 = forms.CharField(widget=forms.PasswordInput(), validators=[password_validation.validate_password])
    password2 = forms.CharField(widget=forms.PasswordInput(), validators=[password_validation.validate_password])

    class Meta:
        parsley_extras = {
                'password1': {
                    'pattern': '^(?=.*[a-zA-Z])(?=\w*[0-9])\w{8,}$',
                    'pattern-message': 'كلمة المرور يجب أن تكون على الأقل 8 أحرف وأرقام و بالأحرف الاتينية',
                },
                'password2': {
                    'equalto': "password1",
                    'equalto-message': "كلمات المرور غير متطابقة",
                },
            }  

    def __init__(self, *args, **kwargs):
        super(RestorePasswordForm, self).__init__(*args, **kwargs)

        for fieldname in ['password1','password2']:
            if fieldname == 'password1':
                self.fields[fieldname].widget.attrs['class'] = 'w3-input w3-border  '
                self.fields[fieldname].widget.attrs['placeholder'] = ''
                self.fields[fieldname].required = True
                self.fields[fieldname].label = 'كلمة المرور الجديدة'
            if fieldname == 'password2':
                self.fields[fieldname].widget.attrs['class'] = 'w3-input w3-border  '
                self.fields[fieldname].widget.attrs['placeholder'] = ''
                self.fields[fieldname].required = True
                self.fields[fieldname].label = 'تأكيد كلمة المرور'
                
    def clean(self):
        cleaned_data = super(RestorePasswordForm, self).clean()
        new_password = cleaned_data.get("password1")
        confirm_password = cleaned_data.get("password2")

        if new_password != confirm_password:
                raise forms.ValidationError(
                "تأكيد كلمة المرور غير متطابقة مع كلمة المرور الجديدة"
                )

        return cleaned_data