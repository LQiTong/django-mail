from rest_framework import serializers
from python_django.models import OutlookMail, hotmail, gmail, net163


# _*_ coding:utf-8 _*_

class OutlookSerializer(serializers.ModelSerializer):
    # 内置类 meta
    class Meta:
        model = OutlookMail
        fields = ('id', 'mail')
