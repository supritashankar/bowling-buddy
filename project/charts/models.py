from django.db import models

# Create your models here.

class MonthlyWeatherByCity(models.Model):
    name = models.CharField(max_length = 10)
    month = models.IntegerField()
    boston_temp = models.DecimalField(max_digits=5, decimal_places=1)
    houston_temp = models.DecimalField(max_digits=5, decimal_places=1)

    def __unicode__(self):
      return self.name
