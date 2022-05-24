from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from django.http.response import JsonResponse
from python_django.models import OutlookMail, hotmail, gmail, net163
from python_django.rest_api.serializers import OutlookSerializer
import base64
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework import status
from python_django.src.outlook_services import Outlook
import re


outlook_services = Outlook()


# Create your views here.

def home(request):
    return HttpResponse('Hello World!!!')


def dashboard(request):
    return HttpResponse("I'm dashboard!!!")


@api_view(['GET', 'POST', 'DELETE'])
def outlook_list(request):
    if request.method == 'GET':
        # 需求：需要一个未使用过的邮箱
        outlook = OutlookMail.objects.all().filter(flag=0)[:1]
        print('outlook --> ', outlook)
        mail = request.query_params.get('mail', None)
        if mail is not None:
            outlook = outlook.filter(mail__contains=mail)

        outlook_serializer = OutlookSerializer(outlook, many=True)
        return JsonResponse(outlook_serializer.data, safe=False)
        # 'safe=False' for objects serialization

    elif request.method == 'POST':
        outlook_data = JSONParser().parse(request)
        outlook_serializer = OutlookSerializer(data=outlook_data)
        if outlook_serializer.is_valid():
            outlook_serializer.save()
            return JsonResponse(outlook_serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(outlook_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        count = OutlookMail.objects.all().delete()
        return JsonResponse({'message': '{} Outlook were deleted successfully!'.format(count[0])},
                            status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def get_code(request):
    if request.method == 'GET':
        mail = request.query_params.get('mail', None)
        app = request.query_params.get('app', None)
        outlook = OutlookMail.objects.values('password').filter(mail=mail).get()
        # 此时获取到的密码是经过 base64 加密过的，需要解密
        password = outlook['password']
        password = str(base64.b64decode(str(password)).decode())
        hasLogin = outlook_services.login(mail, password)
        if hasLogin:
            inbox = outlook_services.select('Inbox')
            hasUnread = outlook_services.hasUnread()
            # 有未读邮件
            if hasUnread:
                latest_unread_mail = outlook_services.unread()
                print('hasUnread --> ', hasUnread)
                mail_from = outlook_services.mailfrom()
                print('mail_from --> ', mail_from)
                hasTiktok = 'tiktok' in mail_from
                hasIns = 'instagram' in mail_from
                decoded = outlook_services.mailbody()
                code = re.compile(r'\d{6}', re.S).findall(str(decoded))[0]
                mail_date = outlook_services.maildate()
                model = OutlookMail.objects.all().filter(mail=mail)
                model.update(flag=1, app=app)
                return JsonResponse({'hasUnread': hasUnread, 'code': code, 'mail_date': mail_date}, status=status.HTTP_200_OK)
            # 没有未读邮件
            else:
                junk = outlook_services.select('Junk')
                print('junk --> ', junk)
                junkHasUnread = outlook_services.hasUnread()
                if junkHasUnread:
                    print('junkHasUnread')
                    latest_unread_mail = outlook_services.unread()
                    print('hasUnread --> ', hasUnread)
                    mail_from = outlook_services.mailfrom()
                    print('mail_from --> ', mail_from)
                    hasTiktok = 'tiktok' in mail_from
                    hasIns = 'instagram' in mail_from
                    decoded = outlook_services.mailbody()
                    code = re.compile(r'\d{6}', re.S).findall(str(decoded))[0]
                    mail_date = outlook_services.maildate()
                    model = OutlookMail.objects.all().filter(mail=mail)
                    model.update(flag=1, app=app)
                    return JsonResponse({'hasUnread': hasUnread, 'code': code, 'mail_date': mail_date},
                                        status=status.HTTP_200_OK)
                else:
                    return JsonResponse({'hasUnread': hasUnread, 'code': '', 'mail_date': ''}, status=status.HTTP_200_OK)
        # 登陆失败
        else:
            return JsonResponse({'message': '{} 登录失败，请稍后再试'.format(mail)}, status=status.HTTP_200_OK)
