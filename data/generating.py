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
            is_markatable=einfo.sell,
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
            r.desc = "bere %s" % naturaljoin(r.consumes.keys())
            if r.needs:
                r.desc += ", potřebuje %s" % naturaljoin(r.needs)
        if r.name is None:
            r.name = "Továrna na %s" % naturaljoin(r.creates.keys())
        nr = Recipe.objects.create(name=r.name, description=r.desc)
    profit = 0
    for name in r.needs:
        nr.ingredient_set.create(recipe=nr,entity=ent(name),type=Ingredient.NEED, amount=1)
        profit -= amount * ent(name).price / 6  # 6 uses of recipe amortizes cost of the tool
    for name, amount in r.consumes.items():
        nr.ingredient_set.create(recipe=nr,entity=ent(name),type=Ingredient.CONSUME,amount=amount)
        profit -= amount * ent(name).price
    for name, amount in r.creates.items():
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

    # TODO: this "minable" list doesn't exist, fix it
    price_sum = sum(f(e.price * e.token_amount) for e in all_goods if e.token_amount > 0)
    for einfo in all_goods:
        if einfo.token_amount > 0:
            count = int(TOKEN_COUNT / price_sum * f(einfo.price * einfo.token_amount))
            for _ in range(count):
                Token.generate_one(e(e.name), e.token_amount)

    return "[ OK ] Token"

from data.blackmarket_offers import generate_blackmarket

@transaction.atomic
def generate_all_data(force = False):
    report = [
        generate_entities(force),
        generate_recipes(force),
        #generate_tokens(force),
        generate_blackmarket(force),
    ]

    return report