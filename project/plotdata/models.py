from django.db import models

class BowlingData(models.Model):
  """ Defines the model of the data values to be displayed """
  
  xvalue = models.CharField(max_length = 20)
  yvalue = models.CharField(max_length = 20)
  zvalue = models.CharField(max_length = 20)
  angle   = models.CharField(max_length = 10)
  accleration = models.CharField(max_length = 10)
  time 	  = models.CharField(max_length = 10)

  def __unicode__(self):
    return "This is the values for this " + str(self.id)
