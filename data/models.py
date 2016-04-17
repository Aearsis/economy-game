from django.db import models
from django.db import transaction
# Create your models here.

from core.models import Entity
from recipes.models import Recipe, Ingredient
from tokens.models import Token
from ekonomicka.utils import naturaljoin

from data.settings import *
from data.blackmarket_pricelist import *

import random

"""
Global, useful shortcut.
"""
def ent(name):
	return Entity.objects.get(name=name)


def generate_entities(force=False):
	if Entity.objects.count() > 0:
		if force:
			Entity.objects.all().delete()
		else:
			return "[SKIP] Entity"

	for name, price in all_pricelist.items():
		Entity.objects.create(name=name, price=price)

	def set_prop(name, prop):
		e = ent(name=name)
		setattr(e, prop, True)
		e.save()

	for n in markatable:
		set_prop(n, 'is_markatable')
	for n in minable:
		set_prop(n, 'is_minable')
	for n in makable:
		set_prop(n, 'is_makable')
	for n in strategical:
		set_prop(n, 'is_strategical')

	for k, v in licences:
		f = ent(v)
		f.licences.add(ent(k))
		f.save()

	return "[ OK ] Entity"

def generate_recipes(force=False):
	if Recipe.objects.count() > 0:
		if force:
			Recipe.objects.all().delete()
		else:
			return "[SKIP] Recipe"

	for r in recipes:
		desc = "bere %s" % naturaljoin(keys(r.consumes))
		if r.needs:
			desc += ", potřebuje %s" % naturaljoin(r.needs)
		nr = Recipe(name="továrna " + naturaljoin(keys(r.creates)), description=desc)
		nr.save()
		profit = 0
		for name in r.needs:
			nr.ingredient_set.create(recipe=nr,entity=ent(name),type=Ingredient.NEED, amount=1)
			profit -= amount * ent(name).price / 6  # 6 uses of recipe amortizes cost of the tool
		for name, amount in r.consumes:
			nr.ingredient_set.create(recipe=nr,entity=ent(name),type=Ingredient.CONSUME,amount=amount)
			profit -= amount * ent(name).price
		for name, amount in r.creates:
			nr.ingredient_set.create(recipe=nr,entity=ent(name),type=Ingredient.CREATE, amount=amount)
			profit += amount * ent(name).price

	print("\t[    ] Profit %f: %s" % (profit, nr.name))

	return "[ OK ] Recipe"

def generate_tokens(force=False):
	TOKEN_COUNT=1024

	if Token.objects.count() > 0:
		if force:
			Token.objects.all().delete()
		else:
			return "[SKIP] Token"

	def f(x):
		import math
		return 1/math.log(x)

	price_sum = sum(f(ent(n).price) for n in minable)
	for n in minable:
		e = ent(n)
		count = int(TOKEN_COUNT / price_sum * f(e.price))
		for _ in range(count):
			Token.generate_one(e)

	return "[ OK ] Token"

from data.blackmarket_offers import generate_blackmarket

@transaction.atomic
def generate_all_data(force = False):
	report = [
		generate_entities(force),
		generate_recipes(force),
		generate_tokens(force),
		generate_blackmarket(force),
 	]

	return report
