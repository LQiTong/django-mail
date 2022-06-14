## python + django + mysql Api 项目

### 环境准备

    APScheduler==3.9.1
    asgiref==3.5.2
    certifi==2022.5.18.1
    charset-normalizer==2.0.12
    coreapi==2.3.3
    coreschema==0.0.4
    Django==4.0.4
    django-apscheduler==0.6.2
    django-cors-headers==3.12.0
    djangorestframework==3.13.1
    docopt==0.6.2
    drf-yasg==1.20.0
    idna==3.3
    inflection==0.5.1
    itypes==1.2.0
    Jinja2==3.1.2
    MarkupSafe==2.1.1
    mysqlclient==2.1.0
    packaging==21.3
    pipreqs==0.4.11
    pyparsing==3.0.9
    pytz==2022.1
    pytz-deprecation-shim==0.1.0.post0
    requests==2.27.1
    ruamel.yaml==0.17.21
    ruamel.yaml.clib==0.2.6
    six==1.16.0
    sqlparse==0.4.2
    tzdata==2022.1
    tzlocal==4.2
    uritemplate==4.1.1
    urllib3==1.26.9
    yarg==0.1.9

    
### 运行
    
    - pip install -r requirements.txt
    - python manage.py migrate  # 创建表结构
    - python manage.py runserver    # 运行项目