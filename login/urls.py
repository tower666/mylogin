from django.urls import path
from . import views

app_name = 'login'

urlpatterns = [

    path('register/', views.register, name='register'),
    path('logout/', views.logout, name='logout'),
    path('comment/', views.comment, name='comment'),
    path('login/', views.login, name='login'),
    path('confirm/', views.confirm, name='confirm'),
    path('success/',views.success,name='success'),

]
