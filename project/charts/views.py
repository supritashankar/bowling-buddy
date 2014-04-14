from django.shortcuts import render
from chartit import DataPool, Chart
from django.shortcuts import render_to_response

from django.template import RequestContext
from charts.models import *

def demo1(request):
  ds = DataPool(
       series=
        [{'options': {
            'source': MonthlyWeatherByCity.objects.all()},
          'terms': [
            'month',
            'houston_temp', 
            'boston_temp']}
         ])

  cht = Chart(
        datasource = ds, 
        series_options = 
          [{'options':{
              'type': 'column',
              'stacking': True},
            'terms':{
              'month': [
                'boston_temp',
                'houston_temp']
              }}],
        chart_options = 
          {'title': {
               'text': 'Weather Data of Boston and Houston'},
           'xAxis': {
                'title': {
                   'text': 'Month number'}}})
  return render_to_response('charts/demo.html', {'weatherchart':cht})

def demo(request):
    #Step 1: Create a DataPool with the data we want to retrieve.
    weatherdata = \
        DataPool(
           series=
            [{'options': {
               'source': MonthlyWeatherByCity.objects.all()},
              'terms': [
                'month',
                'houston_temp',
                'boston_temp']}
             ])
    #Step 2: Create the Chart object
    cht = Chart(
            datasource = weatherdata,
            series_options =
              [{'options':{
                  'type': 'line',
                  'stacking': False},
                'terms':{
                  'month': [
                    'boston_temp',
                    'houston_temp']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Weather Data of Boston and Houston'},
               'xAxis': {
                    'title': {
                       'text': 'Month number'}}})

    #Step 3: Send the chart object to the template.
    return render_to_response('charts/demo.html', {'weatherchart':cht})
