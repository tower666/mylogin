from django.db import models


# Create your models here.
class User(models.Model):
    user_name = models.CharField(max_length=256, unique=True)
    user_email = models.EmailField(unique=True)
    user_password = models.CharField(max_length=256)
    user_c_time = models.DateTimeField(auto_now_add=True)
    email_confirm = models.BooleanField(default=False)

    def __str__(self):
        return self.user_name

    class Meta:
        ordering = ['-user_c_time']
        verbose_name = '用户'
        verbose_name_plural = '用户'

class RegisterCode(models.Model):
    """
        我之前想，一个确认码为什么那么麻烦。
        1,直接用用户被hash后的密码的前几位或后几位不就成了。
            但是我的逻辑是，用户确认邮箱后。才把他的信息传入到数据库。所以没有办法前置获得。
            然后又有一个问题，如果用户要确认邮箱后，才把信息传入到数据库。那我怎么获取user里的创建时间c_time。
            所以。要先传入数据库，再从数据要user_c_time

        2.直接生成一个随便的4位数 不就成了。但是有一点，是发送给用户会写这个确认函的有效期有多少多少天，这就涉及到一个计算。
          计算涉及到这个确认码建立的时间。所以。这个确认码得有一个锚点，意思他是固定的。得存储着！

          所以，想通后，就需要在models里面去实现，创建出一个会传入到数据库里的确认码。好方便后期的计算过期时间！
    """
    code = models.CharField(max_length=256)
    user = models.OneToOneField('User',on_delete=models.CASCADE)
    c_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.user_name + ':' + self.code

    class Meta:
        ordering = ['-c_time']
        verbose_name = '确认码'
        verbose_name_plural = '确认码'
