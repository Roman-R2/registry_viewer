from django.urls import path

from metricsapp import views

app_name = 'metricsapp'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('run_auto_parse', views.RunAutoParseView.as_view(), name='run_auto_parse'),
    path('stop_auto_parse', views.StopAutoParseView.as_view(), name='stop_auto_parse'),
    path('auto_parse_logs', views.AutoParseLogsView.as_view(), name='auto_parse_logs'),
    path('auto_parse_logs_errors', views.AutoParseLogsErrorsView.as_view(), name='auto_parse_logs_errors'),

    path('manual_parse_registry_br', views.ManualParseRegistryBrView.as_view(), name='manual_parse_registry_br'),
    path('manual_parse_registry_br_process', views.ManualParseRegistryBrProcessView.as_view(), name='manual_parse_registry_br_process'),

    path('help', views.AutoParseHelpView.as_view(), name='help'),
]
