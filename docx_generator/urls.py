from django.urls import path

from docx_generator import views

app_name = 'docx_generator'

urlpatterns = [
    path('get_lrp_docx', views.GetLRPDOCX.as_view(), name='get_lrp_docx'),
]
