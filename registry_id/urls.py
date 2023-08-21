from django.urls import path
from rest_framework import routers

from registry_id import views

app_name = 'registry_id'

urlpatterns = [
    path('', views.MainView.as_view(), name='index'),
    path('get_data/', views.RegistryIDViewSet.as_view({'get': 'list'}), name='get_id_data'),
]
