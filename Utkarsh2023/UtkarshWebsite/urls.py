from django.urls import path, include, re_path
from . import views
from django.contrib.sitemaps.views import sitemap
from .sitemaps import StaticViewSitemap

sitemaps = {
    'static': StaticViewSitemap,
}


urlpatterns = [
    path('', views.home, name='homepage'),
    path('registerUser/',views.register, name='regpage'),
    path('forgot-password/',views.ResetPassword),
    path('checkemail/',views.checkemail),
    path('sendOtp/',views.sendOTP),
    # path('verifyUser/', views.verifyUser),
    path('events/', views.EventsPage, name="eventsPage"),
    path('logout/',views.signout),
    path('unenroll/',views.unenroll_user),
    path('RegisterTeam/',views.TeamReg, name="teamRegpage"),
    path("ukidverify/", views.UK_id_verify),
    path("accomodation/", views.AddAccomodation),
    path("contents/", views.ShowStaticContents),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps},
         name='django.contrib.sitemaps.views.sitemap'),
    path("registration-closed", views.RegistrationClose, name="registrationclosed"),
    

]
