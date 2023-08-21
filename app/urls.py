"""app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('api/', include('api.urls', namespace='api')),

    path('api-auth/', include('rest_framework.urls')),
    path('api-auth-token/', obtain_auth_token),

    path('admin/', admin.site.urls),
    path('auth/', include('authapp.urls', namespace='authapp')),
    path('', include('mainapp.urls', namespace='mainapp')),
    path('search/', include('searchapp.urls', namespace='searchapp')),
    path('metrics/', include('metricsapp.urls', namespace='metricsapp')),
    path('docx_generator/', include('docx_generator.urls', namespace='docx_generator')),

    # ------------------------- Реестры программы
    path('registry_lrp/', include('registry_lrp.urls', namespace='registry_lrp')),
    path('registry_lrp_dop/', include('registry_lrp_dop.urls', namespace='registry_lrp_dop')),
    path('registry_id/', include('registry_id.urls', namespace='registry_id')),
    path('registry_zp/', include('registry_zp.urls', namespace='registry_zp')),
    path('registry_br/', include('registry_br.urls', namespace='registry_br')),
    path('registry_rtn_ts/', include('registry_rtn_ts.urls', namespace='registry_rtn_ts')),
    path('registry_state_support/', include('registry_state_support.urls', namespace='registry_state_support')),
]
