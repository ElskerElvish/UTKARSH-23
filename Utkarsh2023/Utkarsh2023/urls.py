from django.conf import settings
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf.urls.static import static

urlpatterns = [
    path('SuperUser/', admin.site.urls),
    path("",include("UtkarshWebsite.urls")),
    re_path(r"^gallery/", include("Gallery.urls") )
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
