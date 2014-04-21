import math
import os, os.path

from django.shortcuts import render
from django.shortcuts import render_to_response
from chartit import DataPool, Chart
from django.contrib.auth.decorators import login_required

from plotdata.models import BowlingData

@login_required
def homepage(request):

  """ Homepage which will display all the the different strikes - from which 2 has to be chosen for comparison """

  frames = []
  for index,name in enumerate(os.listdir('../../sdcard/')):
    frames.append(str(index))
  return render_to_response('plotdata/homepage.html', locals())

@login_required
def data(request, frame1, frame2):

  """ Data that will display results of a particular round """
  """ For SD card on Desktop f = open("/Volumes/NO\ NAME/1.txt", "r") """

 
  no_of_files = len([name for name in os.listdir('../../sdcard/')])
  bend = []
  twist = []
  xvalues = []
  yvalues = []
  zvalues = []
  time_elapsed = []
 
  if no_of_files > 21 or no_of_files == 0:
    return render_to_response('plotdata/error.html')
   
  frame = str(int(frame1) + 1) #Because you storing the index of the array - increment by 1 to get the actual text file
  for i in range(0,2):
      file = frame + ".TXT"
 
      with open('../../sdcard/' + file) as f:
       file_len = len(f.readlines())

      with open('../../sdcard/' + file) as f:

       twist_angle = 0.0
       bend_angle  = 0.0

       for index, line in enumerate(f):
        time_elapsed.append(line.split(',')[0])
        xval 	     = int(line.split(',')[1])
        yval 	     = int(line.split(',')[2])
        zval         = int(line.split(',')[3])
        twist_angle  = ((float(line.split(',')[4]))*180)/math.pi + twist_angle

        if file_len - index < 200:
          bend_angle  = ((float(line.split(',')[5]))*180)/math.pi + bend_angle
      
        """ Do some math to get it in the correct units """
        xval = xval/16384
        yval = yval/16384
        zval = zval/16384

    
        xvalues.append(xval)
        yvalues.append(yval)
        zvalues.append(zval)
         
 	file = name.split('.')[0]

        """
        BowlingData.objects.create(time_elapsed = time_elapsed, 
			 	   xvalue = xval, yvalue = yval, 
				   zvalue = zval, twist = twist, 
			           bend = bend, frame_num=file)
        """
      xv, yv, zv, time_interval, avg_vel = get_velocity(xvalues, yvalues, zvalues, time_elapsed)
      frame = str(int(frame2) + 1)
      twist_angle = twist_angle/1490
      bend_angle = bend_angle/200
     
  print 'Created objects successfully'
  print len(BowlingData.objects.all())

  chart = get_chart()
  return render_to_response('plotdata/data.html', {'datachart':chart})


def get_velocity(xvalues, yvalues, zvalues, time_elapsed):

  """ Return the velocity over time """

  initial_time = 0.0
  velocity_x = 0.0
  velocity_y = 0.0
  velocity_z = 0.0

  velx = []
  vely = []
  velz = []
  time_interval = []

  for index in range(0, len(xvalues)):
    delta_time = float(time_elapsed[index]) - initial_time
    velocity_x = (float(xvalues[index]) * delta_time) + velocity_x
    velocity_y = (float(yvalues[index]) * delta_time) + velocity_y
    velocity_z = (float(zvalues[index]) * delta_time) + velocity_z
    
    if index%100 == 0:
      velx.append(xvalues[index] * delta_time)
      vely.append(yvalues[index] * delta_time)
      velz.append(zvalues[index] * delta_time)
      time_interval.append(time_elapsed[index])

    initial_time = float(time_elapsed[index])   

  total_vel = math.sqrt(float(math.pow(velocity_x,2) + math.pow(velocity_y, 2) + math.pow(velocity_z,2)))
  avg_vel = total_vel/1490.0 
  return velx, vely, velz, time_interval, avg_vel

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

@login_required
def save(request, query):
  """ Function that save the frames in the DB for future retrieval"""
  frames = query.split('&')
 
  for frame in frames:
    file = frame + ".TXT"
    with open('../../sdcard/' + file) as f:
       for line in f:
        time_elapsed = line.split(',')[0]
        xval         = line.split(',')[1]
        yval         = line.split(',')[2]
        zval         = line.split(',')[3]
        twist        = line.split(',')[4]
        bend         = line.split(',')[5]

        """ Do some math to get it in the correct units """
        xval = xval/16384
        yval = yval/16384
        zval = zval/16384

        wrist = (twist*180)/math.pi
        BowlingData.objects.create(time_elapsed = time_elapsed, 
 				   xvalue = xval, yvalue = yval, 
				   zvalue = zval, twist = twist, 
				   bend = bend, frame_num = frame)
 
  return render_to_response('plotdata/save.html')

@login_required
def search(request, from_date, to_date):
  """ Given a from_date and to_date - display all the frames of that given frame """

  return render_to_response('plotdata/search.html') 
