from django.shortcuts import render
from django.shortcuts import render_to_response

# Create your views here.

def homepage(request):

  """ Homepage which will display all the the different times of bowls """
  return render_to_response('plotdata/homepage.html')

def data(request, round):

  """ Data that will display results of a particular round """
  """ For SD card on Desktop f = open("/Volumes/NO\ NAME/1.txt", "r") """

  return render_to_response('plotdata/data.html')
