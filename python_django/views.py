import base64
import calendar
import time
from datetime import datetime

from django.shortcuts import render
from apscheduler.schedulers.background import BackgroundScheduler  # 使用它可以让你的定时任务在后台运行
from django.http.response import JsonResponse
from django.shortcuts import HttpResponse
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
from rest_framework import status
from rest_framework.decorators import api_view

from python_django.models import OutlookMail, hotmail
from python_django.rest_api.serializers import OutlookSerializer, HotMailSerializer
from python_django.src.outlook_services import Outlook
from python_django.utils.get_password_decode import getPassword
from python_django.utils.mail_operation import mail_operation
# 导入网页驱动软件
from selenium import webdriver
from selenium.webdriver.common.by import By
# 导入Image类
from PIL import Image

# 导入网页驱动软件

'''
date:在您希望在某个特定时间仅运行一次作业时使用
interval:当您要以固定的时间间隔运行作业时使用
cron:以crontab的方式运行定时任务
hours:设置以小时为单位的定时器
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


    @register_job(scheduler, "interval", seconds=86400, id="task_time", replace_existing=True, max_instances=100)
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


    @register_job(scheduler, "interval", minutes=30, id="task_login", replace_existing=True, max_instances=100)
    def login():
        query_set = hotmail.objects.all().filter(flag=0)
        bulk = []
        for item in query_set[:200]:
            password = str(base64.b64decode(str(item.password)).decode())
            # print('password --> ', password)
            try:
                outlook_services.login(item.mail, password)
                item.flag = 0
                item.app = ''
                bulk.append(item)
            except Exception as err:
                print('err： {}'.format(item.mail), err)
                item.flag = 2
                item.app = 'handle'
                bulk.append(item)
        hotmail.objects.bulk_update(bulk, ['flag', 'app'])


    @register_job(scheduler, "interval", seconds=86400, id="task_update_status", replace_existing=True, max_instances=100)
    def task_update_status():
        end_time = int(calendar.timegm(time.gmtime())) - 900
        start_time = int(calendar.timegm(time.gmtime())) - (30 * 24 * 60 * 60)
        query_set = hotmail.objects.all().filter(flag=1, status=0, created__istartswith='2022',
                                                 last_get__range=(start_time, end_time))
        query_set.update(flag=0)


    # 监控任务
    register_events(scheduler)

    # 向调度器中添加定时任务
    # scheduler.add_job(refresh_mail_flag)
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
    mail1 = hotmail.objects.all().filter(flag=3)
    _serializer1 = HotMailSerializer(mail1, many=True)
    mail2 = hotmail.objects.all().filter(flag=0)
    _serializer2 = HotMailSerializer(mail2, many=True)
    context = {"mail1": len(_serializer1.data), "mail2": len(_serializer2.data)}
    return render(request, 'mail/dashboard.html', context)


def sign_status(request):
    context = {"total": 0, "charge": 0, "success": 0, "failed": 0, "death": 0}
    return render(request, 'mail/mail.html', context)


@api_view(['POST'])
def get_mail_status(request):
    created = request.POST.get('created')
    start = request.POST.get('start')
    end = request.POST.get('end')
    if start:
        start = start if int(start) >= 10 else '0' + start
        start_time = start + ':00:00'
        start_time_stamp = int((datetime.strptime(created + ' ' + start_time, '%Y-%m-%d %H:%M:%S')).timestamp()) * 1000
    if end:
        end = end if int(end) >= 10 else '0' + end
        end_time = end + ':00:00' if int(end) != 24 else '23:59:59'
        end_time_stamp = int((datetime.strptime(created + ' ' + end_time, '%Y-%m-%d %H:%M:%S')).timestamp()) * 1000

    if start and end:
        startTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(start_time_stamp/1000)))
        endTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(end_time_stamp/1000)))
        if int(start) > int(end):
            return HttpResponse('结束时间需要大于开始时间')

        total = hotmail.objects.all().filter(created__range=(start_time_stamp, end_time_stamp))
    else:
        st = int((datetime.strptime(created + ' 00:00:00', '%Y-%m-%d %H:%M:%S')).timestamp()) * 1000
        et = int((datetime.strptime(created + ' 23:59:59', '%Y-%m-%d %H:%M:%S')).timestamp()) * 1000
        startTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(st/1000)))
        endTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(et/1000)))
        total = hotmail.objects.all().filter(created__range=(st, et))
    charge = total.filter(status=0)
    success = total.filter(status=1)
    failed = total.filter(status=2)
    death = total.filter(status=0, flag=2)
    total_serializer = HotMailSerializer(total, many=True)
    charge_serializer = HotMailSerializer(charge, many=True)
    success_serializer = HotMailSerializer(success, many=True)
    failed_serializer = HotMailSerializer(failed, many=True)
    death_serializer = HotMailSerializer(death, many=True)
    context = {"total": len(total_serializer.data), "charge": len(charge_serializer.data),
               "success": len(success_serializer.data),
               "failed": len(failed_serializer.data), "death": len(death_serializer.data), "startTime": startTime, "endTime": endTime}

    return render(request, 'mail/mail.html', context)


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
        querySet = hotmail.objects.all().filter(flag=0)

        _hot_serializer = HotMailSerializer(querySet[:int(count)], many=True)
        time_now = calendar.timegm(time.gmtime())
        bulk = []
        for item in querySet[:int(count)]:
            item.flag = 3
            item.last_get = time_now
            bulk.append(item)
        hotmail.objects.bulk_update(bulk, ['flag', 'last_get'])

        return JsonResponse(_hot_serializer.data, safe=False)
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
            query_status = request.query_params.get('status', None)
            if query_status is not None:
                if '@outlook.com' in mail:
                    # outlook 邮箱
                    model = OutlookMail.objects.all().filter(mail=mail)
                    model.update(flag=2, app='handle', status=query_status)
                    print('{} 邮箱废弃处理成功！'.format(mail), '注册成功' if int(query_status) == 1 else '邮箱无效')
                    return JsonResponse({'message': '{} 邮箱废弃处理成功！'.format(mail)})
                elif '@hotmail.com' in mail:
                    # hotmail 邮箱
                    model = hotmail.objects.all().filter(mail=mail)
                    model.update(flag=2, app='handle', status=query_status)
                    print('{} 邮箱废弃处理成功！'.format(mail), '注册成功' if int(query_status) == 1 else '邮箱无效')
                    return JsonResponse({'message': '{} 邮箱废弃处理成功！'.format(mail)})
            else:
                if '@outlook.com' in mail:
                    # outlook 邮箱
                    model = OutlookMail.objects.all().filter(mail=mail)
                    model.update(flag=2, app='handle')
                    print('{} 邮箱废弃处理成功！'.format(mail), '注册成功' if int(query_status) == 1 else '邮箱无效')
                    return JsonResponse({'message': '{} 邮箱废弃处理成功！'.format(mail)})
                elif '@hotmail.com' in mail:
                    # hotmail 邮箱
                    model = hotmail.objects.all().filter(mail=mail)
                    model.update(flag=2, app='handle')
                    print('{} 邮箱废弃处理成功！'.format(mail), '注册成功' if int(query_status) == 1 else '邮箱无效')
                    return JsonResponse({'message': '{} 邮箱废弃处理成功！'.format(mail)})
        else:
            return JsonResponse({'message': 'Parameter Error'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_verify(request):
    if request.method == 'GET':
        url = request.query_params.get('url', None)

        if url is not None:
            url_decode = str(base64.b64decode(url).decode())
            print('url_decode', url_decode)
            ch_options = webdriver.ChromeOptions()
            # 为Chrome配置无头模式
            ch_options.add_argument("--headless")  # 隐藏浏览器运行
            ch_options.add_argument('--no-sandbox')  # 给予root执行权限
            ch_options.add_argument('--disable-gpu')
            ch_options.add_argument('--disable-dev-shm-usage')
            # 在启动浏览器时加入配置
            browser = webdriver.Chrome(options=ch_options)
            # 最大化窗口
            browser.maximize_window()
            # 获取此时的时间戳
            time_now = calendar.timegm(time.gmtime())
            try:
                # 这是测试网站
                browser.get(url_decode)
                time.sleep(10)
                # print(browser.page_source)
                log = browser.find_element(By.TAG_NAME, 'html').screenshot(
                    '/www/wwwroot/mail_project/python_django/img/img_full_screen.bmp')
                print('log --> ', log)
                # 定位需要二次截图区块的元素
                dest = browser.find_element(By.XPATH, '//*[@id="captcha-main"]/div[1]')
                # 区块元素左上角在网页中的x坐标
                left = dest.location['x']
                # 区块元素左上角在网页中的y坐标
                top = dest.location['y']
                # 区块元素右下角在网页中的x坐标
                right = dest.location['x'] + dest.size['width']
                # 区块元素右下角在网页中的y坐标
                bottom = dest.location['y'] + dest.size['height']
                # 打开页面的截图
                photo = Image.open('/www/wwwroot/mail_project/python_django/img/img_full_screen.bmp')
                # 根据区块元素坐标实现二次截图
                photo = photo.crop((left, top, right, bottom))
                # 保存二次截图
                photo.save('/www/wwwroot/mail_project/python_django/img/img_{}.bmp'.format(str(time_now)))
                file_url = '/www/wwwroot/mail_project/python_django/img/img_{}.bmp'.format(str(time_now))
                try:
                    r = HttpResponse(open(file_url, 'rb'))
                    r['content_type'] = 'application'
                    r['Content-Disposition'] = 'attachment;filename=img_verify_{}'.format(time_now)
                    return r
                except Exception as err:
                    print('图片下载出错：err --> ', err)
                    return HttpResponse('图片下载失败')
            except Exception as err:
                print('err --> ', err)
                print('session expired. Please change and try again!!!')
                return HttpResponse('session 过期')
        else:
            return JsonResponse({'message': '参数有误，没有传入url'}, status=status.HTTP_400_BAD_REQUEST)
