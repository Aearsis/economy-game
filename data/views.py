#from django.shortcuts import render
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse


from data.models import *


# Create your views here.

@permission_required("control_game")
def index(request):
	generate_all_data()
	return HttpResponse("Právě jsi vygeneroval všechna data.")
