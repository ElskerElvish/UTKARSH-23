from django.db import models

class Gallery(models.Model):
    day = models.IntegerField(default=1)
    title = models.CharField(max_length=100, null=True, blank=True)
    img = models.ImageField(upload_to = "uploads/Gallery")

    @staticmethod
    def get_all(day):
        return Gallery.objects.filter(day=int(day))
    
    @staticmethod
    def get_n(numbers):
        return Gallery.objects.all()[:20]

