from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from django_countries.fields import CountryField
from django.core.exceptions import ValidationError


class SignupForm(UserCreationForm):
    country = forms.CharField(error_messages={
                              'required': 'حقل مطلوب'})
    bio = forms.CharField(widget=forms.TextInput)
    email = forms.CharField(error_messages={
        'unique': 'الايميل موجود', 'invalid': 'الايميل غير صحيح'})
    username = forms.CharField(
        required=True, error_messages={'unique': 'اسم المستخدم موجود'})
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput, error_messages={
                                'password_mismatch': 'غلط'})

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2',
                  'email', 'first_name', 'last_name', 'country', 'bio', )

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)

        for fieldname in ['username', 'password1', 'password2', 'email', 'first_name', 'last_name',  'country', 'bio']:

            self.fields[fieldname].required = False

            if fieldname == 'username':
                self.fields[fieldname].widget.attrs['placeholder'] = 'اسم المستخدم'
                self.fields[fieldname].label = ''
                self.fields[fieldname].widget.attrs['required'] = False
            if fieldname == 'password1':
                self.fields[fieldname].widget.attrs['placeholder'] = 'كلمة المرور'
                self.fields[fieldname].label = ''
                self.fields[fieldname].widget.attrs['required'] = False
            if fieldname == 'password2':
                self.fields[fieldname].widget.attrs['placeholder'] = 'تأكيد كلمة المرور'
                self.fields[fieldname].label = ''
                self.fields[fieldname].widget.attrs['required'] = False
            if fieldname == 'email':
                self.fields[fieldname].widget.attrs['placeholder'] = 'الايميل'
                self.fields[fieldname].label = ''
                self.fields[fieldname].widget.attrs['required'] = False
            if fieldname == 'first_name':
                self.fields[fieldname].widget.attrs['placeholder'] = 'الاسم الاول'
                self.fields[fieldname].label = ''
                self.fields[fieldname].help_text = ''
            if fieldname == 'last_name':
                self.fields[fieldname].widget.attrs['placeholder'] = 'الاسم الاخير'
                self.fields[fieldname].label = ''
                self.fields[fieldname].help_text = ''
            if fieldname == 'country':
                self.fields[fieldname].widget.attrs['placeholder'] = 'الدولة'
                self.fields[fieldname].label = ''
                self.fields[fieldname].widget.attrs['required'] = False
            if fieldname == 'bio':
                self.fields[fieldname].widget.attrs['placeholder'] = 'نبذة عنك'
                self.fields[fieldname].label = ''
                self.fields[fieldname].help_text = ''

            self.fields[fieldname].widget.attrs[
                'oninvalid'] = "this.setCustomValidity('حقل مطلوب')"

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if not password2:
            raise forms.ValidationError("تأكيد كلمة المرور مطلوب")
        if password1 != password2:
            raise forms.ValidationError("كلمات المرور غير متطابقة")
        return password2

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if not password1:
            raise forms.ValidationError("كلمة المرور مطلوبة")

        return password1

    def clean_country(self):
        country = self.cleaned_data.get('country')

        if not country:
            raise forms.ValidationError("حقل مطلوب")

        return country

    def clean_username(self):
        username = self.cleaned_data.get('username')

        if not username:
            raise forms.ValidationError("حقل مطلوب")

        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if not email:
            raise forms.ValidationError("حقل مطلوب")

        return email


class SigninForm(forms.Form):
    username = forms.CharField(error_messages={
        'required': 'حقل مطلوب'})
    password = forms.CharField(widget=forms.PasswordInput, error_messages={
        'required': 'حقل مطلوب'})

    class Meta:
        model = User
        fields = ('username', 'password',)

    def __init__(self, *args, **kwargs):
        super(SigninForm, self).__init__(*args, **kwargs)

        for fieldname in ['username', 'password']:

            self.fields[fieldname].required = False

            if fieldname == 'username':
                self.fields[fieldname].widget.attrs['placeholder'] = 'اسم المستخدم'
                self.fields[fieldname].label = ''
                self.fields[fieldname].widget.attrs['required'] = False
            if fieldname == 'password':
                self.fields[fieldname].widget.attrs['placeholder'] = 'كلمة المرور'
                self.fields[fieldname].label = ''
                self.fields[fieldname].widget.attrs['required'] = False

            self.fields[fieldname].widget.attrs[
                'oninvalid'] = "this.setCustomValidity('حقل مطلوب')"

    def clean_username(self):
        username = self.cleaned_data.get('username')

        if not username:
            raise forms.ValidationError("اسم المستخدم مطلوب")

        return username

    def clean_password(self):
        password = self.cleaned_data.get('password')

        if not password:
            raise forms.ValidationError("كلمة المرور مطلوبة")

        return password
