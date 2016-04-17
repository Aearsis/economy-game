from django.db import models
from django.db import transaction

from core.models import Entity
from recipes.models import Recipe, Ingredient
from tokens.models import Token
from ekonomicka.utils import naturaljoin

from data.static import *

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

	for einfo in all_goods:
		e = Entity.objects.create(
			name=einfo.name,
			price=einfo.price,
			is_strategic=einfo.strategic,
			is_markatable=not einfo.sell,
			is_minable=einfo.token_amount > 0,
		)

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
		if r.desc is None:
			r.desc = "bere %s" % naturaljoin(keys(r.consumes))
			if r.needs:
				r.desc += ", potřebuje %s" % naturaljoin(r.needs)
		if r.name is None:
			r.name = "Továrna na %s" % naturaljoin(keys(r.creates))
		nr = Recipe.objects.create(name=r.name, description=r.desc)
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
		#generate_recipes(force),
		#generate_tokens(force),
		#generate_blackmarket(force),
 	]

	return report
