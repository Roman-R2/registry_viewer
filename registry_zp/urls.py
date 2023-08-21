from django.urls import path

from registry_zp import views

app_name = 'registry_zp'

urlpatterns = [
    path('', views.MainView.as_view(), name='index'),
    path('get_data/', views.RegistryZPViewSet.as_view({'get': 'list'}), name='get_zp_data'),
]
