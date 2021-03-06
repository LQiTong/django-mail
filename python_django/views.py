from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from django.http.response import JsonResponse
from python_django.models import OutlookMail, hotmail, gmail, net163
from python_django.rest_api.serializers import OutlookSerializer, HotMailSerializer
from rest_framework.decorators import api_view
from rest_framework import status
from python_django.src.outlook_services import Outlook
from python_django.utils.get_password_decode import getPassword
from python_django.utils.mail_operation import mail_operation
from apscheduler.schedulers.background import BackgroundScheduler  # 使用它可以让你的定时任务在后台运行
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job

import time
import calendar
import datetime

'''
date:在您希望在某个特定时间仅运行一次作业时使用
interval:当您要以固定的时间间隔运行作业时使用
cron:以crontab的方式运行定时任务
hour:设置以小时为单位的定时器
minutes:设置以分钟为单位的定时器
seconds:设置以秒为单位的定时器
'''

try:
    scheduler = BackgroundScheduler()  # 创建定时任务的调度器对象 --- 实例化调度器
    # 调度器使用 DjangoJobStore()
    scheduler.add_jobstore(DjangoJobStore(), "default")

    '''
    'cron' 方式循环，周一到周日，每天9:30:30执行， id 为工作 ID 作为标记
    @register_job(scheduler, 'cron', day_of_week='mon-sun', hour='9', minute='30',second='30', id='task_time')
    (scheduler, "interval", seconds=5) # 用 interval 方式循环，每 30 秒执行一次
    '''


    @register_job(scheduler, "interval", seconds=1, id="task_time", replace_existing=True)
    def refresh_mail_flag():
        # 定义定时任务
        # 定时每 30 秒执行一次
        # print(f'===================定时器执行开始 {datetime.datetime.now()}===================')
        end_time = int(calendar.timegm(time.gmtime())) - 300
        start_time = int(calendar.timegm(time.gmtime())) - (30 * 24 * 60 * 60)
        ol_models = OutlookMail.objects.all().filter(flag=3, last_get__range=(start_time, end_time))
        hot_models = hotmail.objects.all().filter(flag=3, last_get__range=(start_time, end_time))
        ol_models.update(flag=0)
        hot_models.update(flag=0)
        # print(f'===================定时器执行完毕 {datetime.datetime.now()}===================')


    # 监控任务
    register_events(scheduler)

    # 向调度器中添加定时任务
    # scheduler.add_job(refresh_mail_flag, 'date', args=[100, 'python'])
    # 启动定时器任务调度器工作 --- 调度器开始
    scheduler.start()
except Exception as e:
    print('定时任务异常：%s' % str(e))
    # scheduler.shutdown()

outlook_services = Outlook()


# Create your views here.

def home(request):
    return HttpResponse('Hello World!!!')


def dashboard(request):
    return HttpResponse("I'm dashboard!!!")


def jud_mail(serializer_data):
    if len(serializer_data) != 0:
        timestamp = serializer_data[0]['last_get']
        mail = serializer_data[0]['mail']
        time_now = calendar.timegm(time.gmtime())

        if timestamp is not None:
            time_gap = int(time_now) - int(timestamp)
            if '@outlook.com' in mail:
                # 如果大于等于 5 分钟，那么该邮箱可用
                if time_gap >= 300:
                    model = OutlookMail.objects.all().filter(mail=mail)
                    model.update(last_get=str(time_now))
                    return JsonResponse(serializer_data, safe=False)
                else:
                    model = OutlookMail.objects.all().filter(mail=mail)
                    model.update(flag=3, last_get=str(time_now))
                    outlook = OutlookMail.objects.all().filter(flag=0)[:1]
                    outlook_serializer = OutlookSerializer(outlook, many=True)
                    return jud_mail(outlook_serializer.data)
            elif '@hotmail.com' in mail:
                # 如果大于等于 5 分钟，那么该邮箱可用
                if time_gap >= 300:
                    model = hotmail.objects.all().filter(mail=mail)
                    model.update(last_get=str(time_now))
                    return JsonResponse(serializer_data, safe=False)
                else:
                    model = hotmail.objects.all().filter(mail=mail)
                    model.update(flag=3, last_get=str(time_now))
                    hot = hotmail.objects.all().filter(flag=0)[:1]
                    hot_serializer = HotMailSerializer(hot, many=True)
                    return jud_mail(hot_serializer.data)
        else:
            if '@outlook.com' in mail:
                model = OutlookMail.objects.all().filter(mail=mail)
                model.update(last_get=str(time_now))
                return JsonResponse(serializer_data, safe=False)
            elif '@hotmail.com' in mail:
                model = hotmail.objects.all().filter(mail=mail)
                model.update(last_get=str(time_now))
                return JsonResponse(serializer_data, safe=False)
    else:
        return JsonResponse(serializer_data, safe=False)


def get_mails(data, count):
    if len(data) != 0:
        # 获取 count 数量的邮箱并且标上标记
        mails = list()
        for i in range(int(count)):
            try:
                timestamp = data[i]['last_get']
                mail = data[i]['mail']
                time_now = calendar.timegm(time.gmtime())
                model = hotmail.objects.all().filter(mail=mail)
                model.update(flag=3, last_get=str(time_now))
                _hot_serializer = HotMailSerializer(model, many=True)
                mails.append(_hot_serializer.data[0])
            except Exception as err:
                return JsonResponse(mails, safe=False)
        print('mails --> ', mails)
        return JsonResponse(mails, safe=False)
    else:
        return JsonResponse(data, safe=False)


@api_view(['GET'])
def outlook_list(request):
    if request.method == 'GET':
        count = request.query_params.get('count', None)
        if count is None:
            # 需求：需要一个未使用过的邮箱
            outlook = OutlookMail.objects.all().filter(flag=0)[:1]
            # print('outlook --> ', outlook)

            outlook_serializer = OutlookSerializer(outlook, many=True)
            if len(outlook_serializer.data) != 0:
                return jud_mail(outlook_serializer.data)
                # 'safe=False' for objects serialization
            else:
                hot_mail = hotmail.objects.all().filter(flag=0)[:1]
                # print('hotmail --> ', hot_mail)

                hot_mail_serializer = HotMailSerializer(hot_mail, many=True)
                if len(hot_mail_serializer.data) != 0:
                    return jud_mail(hot_mail_serializer.data)
                else:
                    return JsonResponse(hot_mail_serializer.data, safe=False)
                # return JsonResponse(hot_mail_serializer.data, safe=False)
                # 'safe=False' for objects serialization
        else:
            # 需求，需要 count 数量的可用邮箱
            if str(count).isdigit():
                mailByCount = hotmail.objects.all().filter(flag=0)
                mail_serializer = HotMailSerializer(mailByCount, many=True)
                if len(mail_serializer.data) != 0:
                    return get_mails(mail_serializer.data, count)
                else:
                    return JsonResponse(mail_serializer.data, safe=False)
            else:
                return JsonResponse({'message': '参数输入有误'}, status=status.HTTP_400_BAD_REQUEST)


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
                    model = OutlookMail.objects.all().filter(mail=mail)
                    model.update(flag=0, app='')
                    return JsonResponse({'message': '{} ==== login success!'.format(mail)})
                elif '@hotmail.com' in mail:
                    outlook_services.login(mail, password)
                    model = hotmail.objects.all().filter(mail=mail)
                    model.update(flag=0, app='')
                    return JsonResponse({'message': '{} ==== login success!'.format(mail)})
            except Exception as err:
                print('邮箱登录失败 --> ', err)
                if '@outlook.com' in mail:
                    model = OutlookMail.objects.all().filter(mail=mail)
                    model.update(flag=2, app='handle')
                    return JsonResponse({'message': '{} ==== login failed, please try again later！'.format(mail)},
                                        status=status.HTTP_200_OK)
                elif '@hotmail.com' in mail:
                    model = hotmail.objects.all().filter(mail=mail)
                    model.update(flag=2, app='handle')
                    return JsonResponse({'message': '{} ==== login failed, please try again later！'.format(mail)},
                                        status=status.HTTP_200_OK)
        except OutlookMail.DoesNotExist:
            return JsonResponse({'message': '无对应邮箱数据，请检查邮箱'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
