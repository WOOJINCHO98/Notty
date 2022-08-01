from django.db import models

# Create your models here.
class Route(models.Model):
    start = models.CharField(max_length=30)
    fin = models.CharField(max_length=30)
    
class Account(models.Model):
    title = models.CharField(max_length=200)
    boby = models.TextField()


    def __str__(self):
        return self.title
    