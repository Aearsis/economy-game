#from django.shortcuts import render
from django.http import HttpResponse


from data.models import *


# Create your views here.

def index(request):
	generate_all_data()
	return HttpResponse("Právě jsi vygeneroval všechna data.")
