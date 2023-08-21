from django.urls import path

from registry_state_support import views

app_name = 'registry_state_support'

urlpatterns = [
    path('', views.MainView.as_view(), name='index'),
    path('get_data/', views.RegistryStateSupportViewSet.as_view({'get': 'list'}), name='registry_state_support'),
    path('add/', views.StateSupportFormView.as_view(), name='add_row_registry_state_support'),
]
