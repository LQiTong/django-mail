from django.db import models


# Create your models here.
# _*_ coding:utf-8 _*_

class OutlookMail(models.Model):
    """微软邮箱"""
    mail = models.CharField(verbose_name='邮箱', max_length=255, default='')  # 邮箱账号
    password = models.CharField(verbose_name='密码', max_length=255, default='')  # 邮箱密码
    flag = models.IntegerField(verbose_name='是否使用', default=0)    # 是否使用过 1 已使用 0 未使用 2 废弃锁定
    app = models.CharField(verbose_name='来源', max_length=255, default='')
    last_get = models.IntegerField(verbose_name='上次获取的时间戳', default=0)
    # class Meta:
    #     verbose_name = '微软邮箱'
    #     verbose_name_plural = verbose_name
    #
    # def __str__(self):
    #     return self.password


class hotmail(models.Model):
    """微软邮箱"""
    mail = models.CharField(verbose_name='邮箱', max_length=255, default='')
    password = models.CharField(verbose_name='密码', max_length=255, default='')
    flag = models.IntegerField(verbose_name='是否使用', default=0)  # 是否使用过 1 已使用 0 未使用 2 废弃锁定
    app = models.CharField(verbose_name='来源', max_length=255, default='')
    last_get = models.IntegerField(verbose_name='上次获取的时间戳', default=0)

    class Meta:
        verbose_name = '微软邮箱'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.password


class gmail(models.Model):
    """Gmail"""
    mail = models.CharField(verbose_name='邮箱', max_length=255, default='')
    password = models.CharField(verbose_name='密码', max_length=255, default='')
    flag = models.IntegerField(verbose_name='是否使用', default=0)  # 是否使用过 1 已使用 0 未使用 2 废弃锁定
    app = models.CharField(verbose_name='来源', max_length=255, default='')
    last_get = models.IntegerField(verbose_name='上次获取的时间戳', default=0)

    class Meta:
        verbose_name = '谷歌邮箱'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.password


class net163(models.Model):
    """网易邮箱"""
    mail = models.CharField(verbose_name='邮箱', max_length=255, default='')
    password = models.CharField(verbose_name='密码', max_length=255, default='')
    flag = models.IntegerField(verbose_name='是否使用', default=0)  # 是否使用过 1 已使用 0 未使用 2 废弃锁定
    app = models.CharField(verbose_name='来源', max_length=255, default='')
    last_get = models.IntegerField(verbose_name='上次获取的时间戳', default=0)

    class Meta:
        verbose_name = '网易邮箱'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.password
