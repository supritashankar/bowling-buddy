from django.shortcuts import render
from django.shortcuts import render_to_response

# Create your views here.

def homepage(request):

  """ Homepage which will display all the the different times of bowls """
  return render_to_response('plotdata/homepage.html')
