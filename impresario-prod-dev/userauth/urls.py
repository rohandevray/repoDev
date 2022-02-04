from django.urls import path
from . import views
app_name = 'userauth'

urlpatterns = [
    # path('',views.index,name="index"),
    path('register/',views.register_user,name="register"),
    path('login/',views.login_user,name="login"),
    path('logout/',views.logout_user,name="logout"),
    path('',views.home,name="home"),
    path('menu/',views.menu,name="menu"),
    path('change_password/',views.change_password,name="change_password"),
]
