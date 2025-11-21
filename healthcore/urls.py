from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from documents import views as doc_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', doc_views.home, name='home'),  # Home page
    path('documents/', include('documents.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
