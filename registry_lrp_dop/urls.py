from django.urls import path

from registry_lrp_dop import views

app_name = 'registry_lrp_dop'

urlpatterns = [
    path('', views.MainView.as_view(), name='index'),
    path('get_data/', views.RegistryLRPDopViewSet.as_view({'get': 'list'}), name='get_lrp_dop_data'),
]
