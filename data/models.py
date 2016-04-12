from django.db import models

# Create your models here.

from core.models import Entity

from data.settings import *

entities = {}
def get_or_create_ent(name):
	if name in entities:
		return entities[name]
	e = Entity(name=name,units="ks")
	e.save()
	entities[name] = e
	return e


def generate_entities():
	Entity.objects.all().delete()
	entities = {}
	for n in minable:
		get_or_create_ent(n)

	return
	for k,v in licenced.items():
		lic = [get_or_create_ent(l) for l in k]
		for n in v:
			f = get_or_create_ent(n)
			for l in lic:
				f.licences.add(l)
				l.licenced_entities.add(f)

def generate_all_data():
	generate_entities()
	return "OK"
#print(e)
