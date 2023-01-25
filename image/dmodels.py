from django.db import models


# Create your models here.
class Image(models.Model):
    caption=models.CharField(max_length=100)
    image=models.ImageField()
    title = models.CharField(max_length=50, null=True)
    def __str__(self):
        return  self.caption
