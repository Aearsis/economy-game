from django.db import models
from django.db import transaction
# Create your models here.

from core.models import Entity
from recipes.models import Recipe, Ingredient

from data.settings import *

import random

random.seed(123)

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
	for n in all_goods + tools:
		get_or_create_ent(n)

	for k,v in licences.items():
		lic = [get_or_create_ent(l) for l in k]
		for n in v:
			f = get_or_create_ent(n)
			for l in lic:
				f.licences.add(l)
				l.licenced_entities.add(f)

def generate_recipes():
	Recipe.objects.all().delete()
	for r in recipes:
		nr = Recipe(name="továrna "+r.creates[0],description="TODO")
		nr.save()
		for i in r.needs:
			cons = Ingredient(recipe=nr,entity=get_or_create_ent(i),type=Ingredient.NEED, amount=1)
			cons.save()
		for i in r.consumes:
			cons = Ingredient(
				recipe=nr,
				entity=get_or_create_ent(i),
				type=Ingredient.CONSUME,
				amount=random.randint(1,3)
				)
			cons.save()
		amounts = [1]*len(r.creates) if not r.creates_num else r.creates_num
		for j,i in zip(amounts,r.creates):
			cons = Ingredient(recipe=nr,entity=get_or_create_ent(i),type=Ingredient.CREATE, amount=j)
			cons.save()


@transaction.atomic
def generate_all_data():
#	generate_entities()
	generate_recipes()
	return "OK"
#print(e)
