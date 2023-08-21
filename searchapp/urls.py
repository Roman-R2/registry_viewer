from django.urls import path

from searchapp import views

app_name = 'searchapp'

urlpatterns = [
    path('', views.IndexView.as_view(), name='search_for_snils'),
]
