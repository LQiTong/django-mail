from django.urls import path, include
from . import views

app_name = 'python_django'
urlpatterns = [
    # The home view ('/tutorial/')
    path('', views.home, name='home'),
    # outlook api
    path('getoutlook/', views.outlook_list, name='outlook_list'),
    # hot-mail api
    # path('gethotmail/', views.hot_mail_list, name='hot_mail_list'),
    # get_code api
    path('getcode/', views.get_code, name='get_code'),
    # update mail api
    path('update_mail/', views.update_mail, name='update_mail'),
    # get_verify api
    path('get_verify/', views.get_verify, name='get_verify'),
    # get_mail_status
    path('get_mail_status/', views.get_mail_status, name='get_mail_status'),
    # get_verify_code
    path('get_verify_code/', views.get_verify_code, name='get_verify_code')
]
