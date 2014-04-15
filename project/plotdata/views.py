from django.shortcuts import render
from django.shortcuts import render_to_response
from chartit import DataPool, Chart
from plotdata.models import *
# Create your views here.

def homepage(request):

  """ Homepage which will display all the the different times of bowls """
  return render_to_response('plotdata/homepage.html')

def data(request, round):

  """ Data that will display results of a particular round """
  """ For SD card on Desktop f = open("/Volumes/NO\ NAME/1.txt", "r") """
  time_elapsed = []
  x_axis = []
  y_axis = []
  z_axis = []
  twist = []
  bend = []
  with open('../../1.TXT') as f:
    for line in f:
        time_elapsed = line.split(',')[0]
        xval 	     = line.split(',')[0]
        yval 	     = line.split(',')[1]
        zval         = line.split(',')[2]
        twist 	     = line.split(',')[3]
        bend         = line.split(',')[4]
        
        BowlingData.objects.create(time_elapsed = time_elapsed, xvalue = xval, yvalue = yval, zvalue = zval, twist = twist, bend = bend)


  print 'Created objects successfully'
  print len(BowlingData.objects.all())
  return render_to_response('plotdata/data.html')
