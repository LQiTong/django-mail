from python_django.src.outlook_services import Outlook
from python_django.models import OutlookMail, hotmail
import re
import time

outlook_services = Outlook()


def mail_operation(mail, password, app):
    if '@outlook.com' in mail:
        outlook_services.login(mail, password)
        time.sleep(1)
        outlook_services.select('Inbox')  # 选取收件箱
        has_unread = outlook_services.hasUnread()
        if has_unread:
            outlook_services.unread()   # 选取第一封未读邮件
            mail_body = outlook_services.mailbody()
            print('收件箱邮件主体内容 --> ', mail_body)
            code = re.compile(r'\d{6}', re.S).findall(str(mail_body))[0]
            mail_date = outlook_services.maildate()
            model = OutlookMail.objects.all().filter(mail=mail)
            model.update(flag=1, app=app)
            return {'hasUnread': has_unread, 'code': code, 'mail_date': mail_date}
        else:
            outlook_services.select('Junk')
            junk_has_unread = outlook_services.hasUnread()
            if junk_has_unread:
                outlook_services.unread()
                mail_body = outlook_services.mailbody()
                print('垃圾箱邮件主体内容 --> ', mail_body)
                code = re.compile(r'\d{6}', re.S).findall(str(mail_body))[0]
                mail_date = outlook_services.maildate()
                model = OutlookMail.objects.all().filter(mail=mail)
                model.update(flag=1, app=app)
                return {'hasUnread': junk_has_unread, 'code': code, 'mail_date': mail_date}
            else:
                print('收件箱和垃圾箱均没有未读邮件')
                return {'message': '收件箱和垃圾箱均没有未读邮件，不予取验证码'}
    elif '@hotmail' in mail:
        outlook_services.login(mail, password)
        time.sleep(1)
        outlook_services.select('Inbox')  # 选取收件箱
        has_unread = outlook_services.hasUnread()
        if has_unread:
            outlook_services.unread()  # 选取第一封未读邮件
            mail_body = outlook_services.mailbody()
            print('收件箱邮件主体内容 --> ', mail_body)
            code = re.compile(r'\d{6}', re.S).findall(str(mail_body))[0]
            mail_date = outlook_services.maildate()
            model = hotmail.objects.all().filter(mail=mail)
            model.update(flag=1, app=app)
            return {'hasUnread': has_unread, 'code': code, 'mail_date': mail_date}
        else:
            outlook_services.select('Junk')
            junk_has_unread = outlook_services.hasUnread()
            if junk_has_unread:
                outlook_services.unread()
                mail_body = outlook_services.mailbody()
                print('垃圾箱邮件主体内容 --> ', mail_body)
                code = re.compile(r'\d{6}', re.S).findall(str(mail_body))[0]
                mail_date = outlook_services.maildate()
                model = hotmail.objects.all().filter(mail=mail)
                model.update(flag=1, app=app)
                return {'hasUnread': junk_has_unread, 'code': code, 'mail_date': mail_date}
            else:
                print('收件箱和垃圾箱均没有未读邮件')
                return {'message': '收件箱和垃圾箱均没有未读邮件，不予取验证码'}
