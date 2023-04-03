from django.conf import settings
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf.urls.static import static
from . import views
urlpatterns = [
    re_path(r"", views.photos),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
