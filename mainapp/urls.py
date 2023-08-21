from django.urls import include, path

from mainapp import views

app_name = 'mainapp'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('send_error_message/', views.StoreErrorMessageToDB.as_view(), name='send_error_message'),
]
