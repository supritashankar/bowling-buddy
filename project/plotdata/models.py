from django.db import models
class InstantaenousVelocity(models.Model):

  """ For a given frame define the instantaenous velocity """
  
  velocity 	= models.DecimalField(max_digits = 9, decimal_places = 3)
  time_interval = models.IntegerField()

  def __unicode__(self):
    return 'You have created an instant velocity object'

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
