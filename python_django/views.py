from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from django.http.response import JsonResponse
from python_django.models import OutlookMail, hotmail, gmail, net163
from python_django.rest_api.serializers import OutlookSerializer
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework import status


# Create your views here.

def home(request):
    return HttpResponse('Hello World!!!')


def dashboard(request):
    return HttpResponse("I'm dashboard!!!")


@api_view(['GET', 'POST', 'DELETE'])
def outlook_list(request):
    if request.method == 'GET':
        outlook = OutlookMail.objects.all()
        print('GET')
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
