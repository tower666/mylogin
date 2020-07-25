from django import forms
from captcha.fields import CaptchaField


class RegisterForm(forms.Form):
    form_email = forms.EmailField(label='邮箱',
                                  widget=forms.EmailInput(attrs={'class': 'form-control'}))
    form_username = forms.CharField(label='用户名', max_length=100,
                                    widget=forms.TextInput(attrs={'class': 'form-control'}))
    form_password1 = forms.CharField(label='密码', max_length=256,
                                     widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    form_password2 = forms.CharField(label='确认密码', max_length=256,
                                     widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    form_captcha = CaptchaField(label='验证码')

class LoginForm(forms.Form):
    email = forms.EmailField(label='邮箱',
                                  widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='密码', max_length=256,
                                     widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    form_captcha = CaptchaField(label='验证码')