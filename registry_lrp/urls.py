from django.urls import path

from registry_lrp import views

app_name = 'registry_lrp'

urlpatterns = [
    path('', views.MainView.as_view(), name='index'),
    path('get_data/', views.RegistryLRPViewSet.as_view({'get': 'list'}), name='get_lrp_data'),
]
