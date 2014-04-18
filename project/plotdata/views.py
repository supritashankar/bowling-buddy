import math
import os, os.path

from django.shortcuts import render
from django.shortcuts import render_to_response
from chartit import DataPool, Chart

from plotdata.models import BowlingData

def homepage(request):

  """ Homepage which will display all the the different strikes - from which 2 has to be chosen for comparison """
  frames = []
  for index,name in enumerate(os.listdir('../../sdcard/')):
    frames.append(str(index))
  return render_to_response('plotdata/homepage.html', locals())

def data(request, frame1, frame2):

  """ Data that will display results of a particular round """
  """ For SD card on Desktop f = open("/Volumes/NO\ NAME/1.txt", "r") """

  time_elapsed = []
  x_axis = []
  y_axis = []
  z_axis = []
  twist = []
  bend = []
  
  no_of_files = len([name for name in os.listdir('../../sdcard/') if os.path.isfile(name)])
  
  if no_of_files > 21 or no_of_files == 0:
    return render_to_response('plotdata/error.html')

  for name in os.listdir('../../sdcard/'):
    if os.path.isfile(name) and os.stat(name)[6]==0: 
      with open('../../sdcard/1.TXT') as f:
       for line in f:
        time_elapsed = line.split(',')[0]
        xval 	     = line.split(',')[1]
        yval 	     = line.split(',')[2]
        zval         = line.split(',')[3]
        twist 	     = line.split(',')[4]
        bend         = line.split(',')[5]
      
        """ Do some math to get it in the correct units """
        xval = xval/16384
        yval = yval/16384
        zval = zval/16384

        wrist = (twist*180)/math.pi 
        BowlingData.objects.create(time_elapsed = time_elapsed, xvalue = xval, yvalue = yval, zvalue = zval, twist = twist, bend = bend)

  print 'Created objects successfully'
  print len(BowlingData.objects.all())


  chart = get_chart()
  return render_to_response('plotdata/data.html', {'datachart':chart})

def get_chart():

  """ Return the data in the proper format needed for the charts """


  bowlingdata = \
        DataPool(
           series=
            [{'options': {
               'source': BowlingData.objects.all()},
              'terms': [
                'time_elapsed',
                'xvalue',
                'yvalue']}
             ])


  cht = Chart(
            datasource = bowlingdata,
            series_options =
              [{'options':{
                  'type': 'line',
                  'stacking': False},
                'terms':{
                  'time_elapsed': [
                    'xvalue',
                    'yvalue']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Bowling Data of x-axis and y-axis'},
               'xAxis': {
                    'title': {
                       'text': 'Time elapsed'}}}) 
  return cht

def save(request, query):
  """ Function that save the frames in the DB for future retrieval"""

  return render_to_response('plotdata/save.html')
