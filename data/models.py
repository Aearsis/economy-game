from django.db import models
from django.db import transaction
# Create your models here.

from core.models import Entity
from recipes.models import Recipe, Ingredient

from data.settings import *
from data.blackmarket_pricelist import *

import random

random.seed(123)

class EntitiesBuffer:
	
	def __init__(self):
		Entity.objects.all().delete()
		self.mapping = {}

	def create_entity(self, name, units="ks"):
		print(name)
		if name in self.mapping:
			raise ValueError("already created")
		e = Entity(name=name, units=units)
		e.price = all_pricelist[name]
		e.save()
		self.mapping[name] = e
		return e

	def get_or_create_ent(self, name, units="ks"):
		if not name in self.mapping:
			return self.create_entity(name, units)
		return self.get_entity(name)

	def get_entity(self, name):
		return self.mapping[name]

	def set_price(self, name, price):
		if name=="Kel":
			for i in range(10):
				print("je tu kel!!!")
		self.mapping[name].price = price

	def get_price(self, name):
		print(name)
		return self.mapping[name].price


def generate_entities():
	buf = EntitiesBuffer()
	for n in all_goods:
		buf.create_entity(n)

	return buf

def generate_licences(buf):
	print(licences)
	for k,v in licences:
		print(k,v)
		l = buf.get_or_create_ent(k)
		f = buf.get_or_create_ent(v)
		f.licences.add(l)
		l.licenced_entities.add(f)
		f.save()
		l.save()
	return buf

def generate_recipes(buf):
	Recipe.objects.all().delete()
	for r in recipes:
		desc = "bere "+" ".join(r.consumes)+", potřebuje "+" ".join(r.needs)
		nr = Recipe(name="továrna "+" ".join(r.creates),description=desc)
		nr.save()
		for i in r.needs:
			cons = Ingredient(recipe=nr,entity=buf.get_or_create_ent(i),type=Ingredient.NEED, amount=1)
			cons.save()
		for i in r.consumes:
			cons = Ingredient(
				recipe=nr,
				entity=buf.get_or_create_ent(i),
				type=Ingredient.CONSUME,
				amount=random.randint(1,3)
				)
			cons.save()
		for j,i in zip(r.creates_num,r.creates):
			cons = Ingredient(recipe=nr,entity=buf.get_or_create_ent(i),type=Ingredient.CREATE, amount=j)
			cons.save()

	return buf

def generate_pricelist(buf):
	
	print(all_pricelist)
	for k,v in all_pricelist.items():
		buf.set_price(k, v)

	for e in all_goods:
		print(buf.get_entity(e).price)

	return buf

from data.blackmarket_offers import generate_blackmarket

@transaction.atomic
def generate_all_data():
	buf = generate_entities()
	buf = generate_licences(buf)
	buf = generate_recipes(buf)
	buf = generate_pricelist(buf)

	buf.get_entity("Kel").price
	for x in all_goods:
		try:
			buf.get_entity(x).price
		except AttributeError:
			print("entity %s doesn't have price" % x)
			raise

	generate_blackmarket(buf)
