from django.contrib import admin
from django.urls import path, include 
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    
    path('restaurante/', include('restaurant.urls')),
    path('admin/', admin.site.urls),    
    path('', include('store.urls')),
]

# Isso permite que o Django sirva os arquivos de mídia em modo DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)