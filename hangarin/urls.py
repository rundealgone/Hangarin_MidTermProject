from django.contrib import admin
from django.urls import path, include

admin.site.site_header = "Hangarin Admin"
admin.site.site_title = "Hangarin"
admin.site.index_title = "Task Manager Administration"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('pwa.urls')),
    path('', include('tasks.urls')),
]
