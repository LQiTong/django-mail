from django.urls import path, include
from . import views

app_name = 'python_django'
urlpatterns = [
    # The home view ('/tutorial/')
    path('', views.home, name='home'),
    # outlook api
    path('getoutlook/', views.outlook_list, name='outlook_list'),
    # get_code api
    path('getcode/', views.get_code, name='get_code'),
]
