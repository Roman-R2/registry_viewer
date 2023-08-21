from django.urls import path

from registry_br import views

app_name = 'registry_br'

urlpatterns = [
    path('', views.MainView.as_view(), name='index'),
    path('get_data/', views.RegistryBRViewSet.as_view({'get': 'list'}), name='get_br_data'),
]
