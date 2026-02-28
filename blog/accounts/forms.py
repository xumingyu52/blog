from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm

class CustomUserCreationForm(UserCreationForm):
    avatar = forms.ImageField(
        required=False,
        label='用户头像',
    )

    email = forms.EmailField(
        required=False,
        label = '邮箱',
    )

    class Meta:
        model = CustomUser
        fields = ('username','email','avatar','password1','password2')

        labels = {
            'username': '用户名',
            'password1': '密码',
            'password2': '确认密码',
        }

    # 新增：邮箱验证
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            if '@' not in email or '.' not in email:
                raise forms.ValidationError("请输入有效的邮箱地址！")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)

        user.avatar = self.cleaned_data.get('avatar', user.avatar)  # 头像（如果没传，用默认值）
        user.email = self.cleaned_data['email']  # 邮箱

        if commit:
            user.save()

        return user

class CustomUserChangeForm(UserChangeForm):
    """修改除了密码以外的信息"""
    password = None

    avatar = forms.ImageField(
        required=False,
        label='用户头像',
    )

    email = forms.EmailField(
        required=False,
        label = '邮箱',
    )

    class Meta:
        model = CustomUser
        fields = ('username','email','avatar')

        labels = {
            'username': '用户名',
            'email': '邮箱',
            'avatar': '用户头像',
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            if '@' not in email or '.' not in email:
                raise forms.ValidationError("请输入有效的邮箱地址！")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        current_user = self.instance
        if username != current_user.username and CustomUser.objects.filter(username=username).exists():
            raise ValidationError("该用户名已被占用！")
        return username


    def save(self, commit=True):
        user = super().save(commit=False)

        new_avatar = self.cleaned_data.get('avatar')  # 头像（如果没传，用默认值）
        user.email = self.cleaned_data['email']  # 邮箱

        if new_avatar:
            user.avatar = new_avatar

        if commit:
            user.save()

        return user
    
    

class CustomPasswordChangeForm(PasswordChangeForm):
    """修改密码表单（极简版）"""
    old_password = forms.CharField(label='旧密码', widget=forms.PasswordInput)
    new_password1 = forms.CharField(label='新密码', widget=forms.PasswordInput)
    new_password2 = forms.CharField(label='确认新密码', widget=forms.PasswordInput)

    # 可选：加自定义密码验证（比如密码长度）
    def clean_new_password1(self):
        new_pwd = self.cleaned_data.get('new_password1')
        if len(new_pwd) < 8:
            raise forms.ValidationError("新密码至少8位！")
        return new_pwd

        
