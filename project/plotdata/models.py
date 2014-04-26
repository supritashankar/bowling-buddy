from django.db import models
class InstantaenousVelocity(models.Model):

  """ For a given frame define the instantaenous velocity """
  
  velocity 	= models.DecimalField(max_digits = 9, decimal_places = 3)
  time_interval = models.IntegerField()

  def __unicode__(self):
    return 'You have created an instant velocity object'

class Angles(models.Model):
  """ To display the angle for the graph """
  
  twist         = models.DecimalField(max_digits = 9, decimal_places = 3)
  bend          = models.DecimalField(max_digits = 9, decimal_places = 3)
  time_interval = models.IntegerField()

  def __unicode__(self):
    return "Created angles successfully"

class DistancePlot(models.Model):
  """ To plot the distance """

  distancex = models.DecimalField(max_digits = 9, decimal_places = 3)
  distancey = models.DecimalField(max_digits = 9, decimal_places = 3)
  distancez = models.DecimalField(max_digits = 9, decimal_places = 3)
  time_interval = models.IntegerField()

  def __unicode__(self):
    return "Distance plot success"

class BowlingData(models.Model):
  """ Defines the model of the data values to be displayed """

  timetaken        = models.IntegerField()
  frame_num        = models.CharField(max_length = 2)
  velocity         = models.ManyToManyField(InstantaenousVelocity)
  average_velocity = models.DecimalField(max_digits = 9, decimal_places = 3)
  created          = models.DateField(auto_now_add=True)

  def __unicode__(self):
    return "This is the values for this " + str(self.id)
