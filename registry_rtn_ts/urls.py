from django.urls import path

from registry_rtn_ts import views

app_name = 'registry_rtn_ts'

urlpatterns = [
    path('', views.MainView.as_view(), name='index'),
    path('get_data/', views.RegistryRtnTsViewSet.as_view({'get': 'list'}), name='registry_rtn_ts'),
]
