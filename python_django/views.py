from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from django.http.response import JsonResponse
from python_django.models import OutlookMail, hotmail, gmail, net163
from python_django.rest_api.serializers import OutlookSerializer, HotMailSerializer
from rest_framework.decorators import api_view
from rest_framework import status
from python_django.src.outlook_services import Outlook
from python_django.utils.get_password_decode import getPassword
from python_django.utils.mail_operation import mail_operation

outlook_services = Outlook()


# Create your views here.

def home(request):
    return HttpResponse('Hello World!!!')


def dashboard(request):
    return HttpResponse("I'm dashboard!!!")


@api_view(['GET'])
def outlook_list(request):
    if request.method == 'GET':
        try:
            # 需求：需要一个未使用过的邮箱
            outlook = OutlookMail.objects.all().filter(flag=0)[:1]
            print('outlook --> ', outlook)
            mail = request.query_params.get('mail', None)
            if mail is not None:
                outlook = outlook.filter(mail__contains=mail)

            outlook_serializer = OutlookSerializer(outlook, many=True)
            return JsonResponse(outlook_serializer.data, safe=False)
            # 'safe=False' for objects serialization
        except OutlookMail.DoesNotExist:
            hot_mail = hotmail.objects.all().filter(flag=0)[:1]
            print('hotmail --> ', hot_mail)
            mail = request.query_params.get('mail', None)
            if mail is not None:
                hot_mail = hot_mail.filter(mail__contains=mail)

            hot_mail_serializer = HotMailSerializer(hot_mail, many=True)
            return JsonResponse(hot_mail_serializer.data, safe=False)
            # 'safe=False' for objects serialization


@api_view(['GET'])
def get_code(request):
    if request.method == 'GET':
        mail = request.query_params.get('mail', None)
        app = request.query_params.get('app', None)
        if not mail or not app:
            return JsonResponse({'message': 'Parameter Error'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            password = getPassword(mail)
            try:
                response = mail_operation(mail, password, app)
                return JsonResponse(response, status=status.HTTP_200_OK)

            except Exception as err:
                print('邮箱登录失败 --> ', err)
                if '@outlook.com' in mail:
                    model = OutlookMail.objects.all().filter(mail=mail)
                    model.update(flag=2, app=app)
                    return JsonResponse({'message': '{} 邮箱登陆失败，请稍后再试！'.format(mail)}, status=status.HTTP_200_OK)
                elif '@hotmail.com' in mail:
                    model = hotmail.objects.all().filter(mail=mail)
                    model.update(flag=2, app=app)
                    return JsonResponse({'message': '{} 邮箱登陆失败，请稍后再试！'.format(mail)}, status=status.HTTP_200_OK)
        except OutlookMail.DoesNotExist:
            return JsonResponse({'message': '无对应邮箱数据，请检查邮箱'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def update_mail(request):
    if request.method == 'GET':
        mail = request.query_params.get('mail', None)
        if mail is not None:
            if '@outlook.com' in mail:
                # outlook 邮箱
                model = OutlookMail.objects.all().filter(mail=mail)
                model.update(flag=2, app='handle')
                print('{} 邮箱废弃处理成功！'.format(mail))
                return JsonResponse({'message': '{} 邮箱废弃处理成功！'.format(mail)})
            elif '@hotmail.com' in mail:
                # hotmail 邮箱
                model = hotmail.objects.all().filter(mail=mail)
                model.update(flag=2, app='handle')
                print('{} 邮箱废弃处理成功！'.format(mail))
                return JsonResponse({'message': '{} 邮箱废弃处理成功！'.format(mail)})
        else:
            return JsonResponse({'message': 'Parameter Error'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def test_login(request):
    if request.method == 'GET':
        mail = request.query_params.get('mail', None)
        if not mail:
            return JsonResponse({'message': 'Parameter Error'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            password = getPassword(mail)
            try:
                if '@outlook.com' in mail:
                    outlook_services.login(mail, password)
                    return JsonResponse({'message': '{} 登陆成功!'.format(mail)})
                elif '@hotmail.com' in mail:
                    outlook_services.login(mail, password)
                    return JsonResponse({'message': '{} 登陆成功!'.format(mail)})
            except Exception as err:
                print('邮箱登录失败 --> ', err)
                if '@outlook.com' in mail:
                    model = OutlookMail.objects.all().filter(mail=mail)
                    model.update(flag=2, app='handle')
                    return JsonResponse({'message': '{} 邮箱登陆失败，请稍后再试！'.format(mail)}, status=status.HTTP_200_OK)
                elif '@hotmail.com' in mail:
                    model = hotmail.objects.all().filter(mail=mail)
                    model.update(flag=2, app='handle')
                    return JsonResponse({'message': '{} 邮箱登陆失败，请稍后再试！'.format(mail)}, status=status.HTTP_200_OK)
        except OutlookMail.DoesNotExist:
            return JsonResponse({'message': '无对应邮箱数据，请检查邮箱'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

