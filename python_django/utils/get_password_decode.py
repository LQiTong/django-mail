from python_django.models import OutlookMail, hotmail
import base64


def getPassword(mail):
    # hot_mail 邮箱
    hot_mail = hotmail.objects.all().values('password').filter(mail=mail).get()
    # 此时获取到的是加密过后的邮箱密码
    password = hot_mail['password']
    password = str(base64.b64decode(str(password)).decode())
    print('{} 对应的邮箱密码为 --> '.format(mail), password)
    return password
