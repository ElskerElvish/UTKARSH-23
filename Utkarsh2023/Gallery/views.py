from django.shortcuts import render
from . import models
# Create your views here.
def photos(request):
    day = request.GET.get('day')
    if day == None:
        ims  = models.Gallery.get_n(20)
        return render(request, "gallery.html", {"image":ims,"days":[1,2,3],"filter":False }, )
    else:
        ims  = models.Gallery.get_all(day)
        return render(request, "gallery.html", {"image":ims,"filter":True }, )