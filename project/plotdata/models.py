from django.db import models

class BowlingData(models.Model):
  """ Defines the model of the data values to be displayed """

  timetaken        = models.IntegerField()
  twist            = models.DecimalField(max_digits = 9, decimal_places = 3)
  bend             = models.DecimalField(max_digits = 9, decimal_places = 3)
  frame_num        = models.CharField(max_length = 2)
  velocity         = models.ManyToManyField(InstantaenousVelocity)
  average_velocity = models.DecimalField(max_digits = 9, decimal_places = 3)
  created          = models.DateField(auto_now_add=True)

  def __unicode__(self):
    return "This is the values for this " + str(self.id)

class InstantaenousVelocity(models.Model):

  """ For a given frame define the instantaenous velocity """

  xvalue        = models.IntegerField()
  yvalue        = models.IntegerField()
  zvalue        = models.IntegerField()
  time_interval = models.IntegerField()
