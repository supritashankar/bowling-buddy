from django.db import models

class BowlingData(models.Model):
  """ Defines the model of the data values to be displayed """

  time_elapsed = models.IntegerField()
  xvalue       = models.IntegerField()
  yvalue       = models.IntegerField()
  zvalue       = models.IntegerField()
  twist        = models.DecimalField(max_digits = 9, decimal_places = 3)
  bend         = models.DecimalField(max_digits = 9, decimal_places = 3)
  created      = models.DateField(auto_now_add=True)
  frame_num    = models.CharField(max_length = 2)

  def __unicode__(self):
    return "This is the values for this " + str(self.id)
