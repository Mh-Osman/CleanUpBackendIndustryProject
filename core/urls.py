"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
# =======
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="CleanUpBackend API",
      default_version='v1',
      description="API documentation for CleanUpBackend",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)
# >>>>>>> gani

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/users/', include('users.urls')),
    path('api/v1/', include('clientProfiles.urls')),
    path('api/v1/', include('employeeProfiles.urls')),
    path('api/v1/task/',include('assign_task_employee.urls')), 
    path('api/v1/plan/',include('plan.urls')),
    path('api/v1/invoice_request_from_client/',include('invoice_request_from_client.urls')),
    path('api/v1/', include('locations.urls')),
    path('api/v1/', include('services_pakages.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # <<<<<<< gani
   path('api/v1/', include('google_map.urls')),
   #salah uddin
   path('api/v1/all_history/',include('all_history.urls')),
   path('api/v1/dashboard/',include('admin_dashboard.urls')),
]
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

