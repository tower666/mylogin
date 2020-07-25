from django.shortcuts import render, redirect
from . import forms, models
import hashlib

def hash_code(s,salt='tower'):
    h =hashlib.sha256()   # 构造了hash对象
    s+=salt
    h.update(s.encode())
    return h.hexdigest()  # 获得摘要

def send_email(email, code):
    # from mylogin import settings   # 要导入settings不能这么随便！
    from django.conf import settings
    from django.core.mail import EmailMultiAlternatives


    subject = '来自tower的邮箱确认'
    text_content = '''感谢注册tower网站，这个网站纯属无聊建设\
                    如果你看到这条消息，说明你的邮箱服务器不提供HTML链接功能，请联系管理员！
                    '''

    html_content = """<p>点击链接<a href='http://{}/login/confirm/?code={}'>一个链接</a>完成注册</p>\
                    <p>此链接有效期为{}天</p>
                    """.format('127.0.0.1:8000', code,settings.CONFIRM_DAYS)

    msg = EmailMultiAlternatives(subject,text_content,from_email=settings.EMAIL_HOST_USER, to=[email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

def confirm(request):
    """
    在send_email视图中，构造了一个点击链接
    <a href='http://{}/login/success/?code={}'>一个链接</a>
    这个用get来获取

    """
    code = request.GET['code']  # 就是去获取register视图里的code=make_confirm_code(new_user)
    print(code)  # 去注册视图里看一下是不是一样的
    try:
        confirm_code = models.RegisterCode.objects.get(code=code)  # 在数据库中，已经生成了相应的user和user对应的code。找出来
    except:
        message = '请检查用户是否注册信息填写准确！'
        return render(request, 'login/register.html', locals())

    # 接下来看看验证码过期了吗
    import datetime
    c_time = confirm_code.c_time   # 得到这个码原本创建的时间
    now = datetime.datetime.now()
    if now >= c_time + datetime.timedelta(3):  # c_time + datetime.timedelta(3) 表示码创建时间3天后
        confirm_code.user.delete()     # 如果验证码失效了，我就把他原来的注册信息全部删掉
        message='验证码已经失效，请重新注册！'
        return render(request, 'login/register.html', locals())
    else:
        confirm_code.user.email_confirm = True
        # 此处有一个问题。我上面之前是models.RegisterCode.objects.get(code=code) 用的是filter
        # 然后email_confirm就没有定位到正确的User里。变成get就可以了？？？？
        confirm_code.user.save()   # 保存confirm_code.user.email_confirm = True的更改。
        # confirm_code.delete()    # 删掉这个实例。为什么要删掉
        message='感谢确认，恭喜注册成功，请登录'
        return render(request, 'login/success.html', locals())

def make_confirm_code(user):   # 根据用户来生成
    import datetime
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    code = hash_code(user.user_name, now)   # 此时 加盐是 now这个字符串了。不是tower这个盐了
    models.RegisterCode.objects.create(code=code, user=user)
    return code

def index(request):
    return render(request, 'login/index.html', locals())


def register(request):
    if request.session.get('is_login', None):   # 为什么不直接request.session['is_login']
        return redirect('login:comment')

    if request.method == 'POST':
        register_form = forms.RegisterForm(request.POST)

        if register_form.is_valid():
            form_email = register_form.cleaned_data.get('form_email')
            form_username = register_form.cleaned_data.get('form_username')
            form_password1 = register_form.cleaned_data.get('form_password1')
            form_password2 = register_form.cleaned_data.get('form_password2')

            if form_password1 != form_password2:
                message = '密码两次输入不一致！'
                return render(request, 'login/register.html', locals())

            else:

                same_email = models.User.objects.filter(user_email=form_email)
                if same_email:
                    message = '邮箱已注册！'
                    return render(request, 'login/register.html', locals())

                same_name = models.User.objects.filter(user_name=form_username)
                if same_name:
                    message = '名字已经被注册！'
                    return render(request, 'login/register.html', locals())

                new_user = models.User()
                new_user.user_name = form_username
                new_user.user_email = form_email
                new_user.user_password = hash_code(form_password1)
                new_user.save()

                code=make_confirm_code(new_user)
                print(code)
                send_email(form_email, code)
                message='请前往邮箱确认'
                return render(request,'login/confirm.html', locals())   # 用这个视html绑定的视图来处理邮箱确认的问题

                # 发送邮件给客户。
                # 客户点击后。把布尔值改变为true后，表示邮件确认成功
                # 如果邮件确认成功了。就把客户的相关信息添加到数据库。否则就不添加。
                # 为什么要放在new_user = models.User()后面，参考models里的注释

        else:
            return render(request, 'login/register.html', locals())

    register_form = forms.RegisterForm()
    return render(request, 'login/register.html', locals())


def login(request):
    if request.session.get('is_login', None):   # 为什么不直接request.session['is_login】
        return redirect('login:comment')
    if request.method == 'POST':
        login_form = forms.LoginForm(request.POST)

        if login_form.is_valid():
            email = login_form.cleaned_data.get('email')
            password = login_form.cleaned_data.get('password')

            try:
                user = models.User.objects.get(user_email=email)

            except:
                message = '邮箱没有注册'
                return render(request, 'login/login.html', locals())

            if not user.email_confirm:
                message='邮箱还没有确认'
                return render(request, 'login/login.html', locals())


            if user.user_password == hash_code(password):
                request.session['is_login'] = True
                request.session['name'] = user.user_name
                request.session['email'] = user.user_email
                # request.session['user_id']=user.id
                return redirect('login:comment')

            else:
                message = '密码错误！'
                return render(request, 'login/login.html', locals())


        else:
            return render(request, 'login/login.html', locals())

    login_form = forms.LoginForm()
    return render(request, 'login/login.html', locals())


def logout(request):
    if request.session['is_login']:   # 这里有变化！
        request.session.flush()
        return redirect('/')


def comment(request):
    return render(request, 'login/comment.html')

def success(request):
    pass