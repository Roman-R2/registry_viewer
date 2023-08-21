from django.urls import path

from authapp import views

app_name = 'authapp'

urlpatterns = [
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('register/', views.register, name='register'),
    path('users/', views.ActiveUsers.as_view(), name='users'),
    path('users/not-active', views.NotActiveUsers.as_view(), name='not_active_users'),
    path('user/delete/<pk>/', views.DeleteAppExtendedUser.as_view(), name='delete_user'),
    path('user/refresh/<pk>/', views.RefreshAppExtendedUser.as_view(), name='refresh_user'),
    path('user/permissions/<pk>/', views.PermissionsAppExtendedUser.as_view(), name='permissions_user'),

    path('users/get_data/', views.UserJSONViewSet.as_view({'get': 'list'}), name='get_user_data'),
]
