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
    # test_login api
    path('test_login/', views.test_login, name='test_login')
]
