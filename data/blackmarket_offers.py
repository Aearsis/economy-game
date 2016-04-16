from data.settings import *
from data.models import *
from data.blackmarket_pricelist import *

import datetime

from auctions.models import *
from core.models import *

from random import *

from math import isinf

seed(123)

def randfloat(a,b):
	assert a<=b
	return a+random()*(b-a)

def fair_status():
	return choice(["obchod proběhl v pořádku",
#		"prodávající měl asi 3 dny zpoždění, ale zboží je nakonec v pořádku",
		])

def fake_status():
	return choice(["smůla! byl to podvod!"])

def seller_name():
	return choice(["diskrétní obchodník z černého trhu",
		"Mr. Stone","Dr. Kámen","anonymní obchodník","nikdo"])


class SellerBase:
	'''abstract class'''

	def __init__(self, buf):
		print("jsem v seller konstruktoru")
		self.game_len = Game.the_row().length
		self.model = buf
		self.seller_name = "base"

	# abstract method
	def buying_entities(self,time):
		raise NotImplemented()

	def selling_entities(self,time):
		raise NotImplemented()

	def create_auction_object(self,entity="Kel"):
		print(self.model)
		a = BlackAuction(
			begin=datetime.timedelta(seconds=1),
			end=None,
			var_entity=self.model.get_entity(entity),
			var_min = 10,
			seller_name=seller_name(),
			status_text=fair_status()
			)
		return a

	def price(self, entity):
		print(entity)
		return self.model.get_price(entity)

	def get_items_to_price(self, price, items):
		'''choices random items whose sum of price is as nearest as posible to
		price

		it chooses it 10-times randomly and returns the best attempt
		'''

		print("tady",items)
		m_items = []
		m_val = float("-inf")
		for _ in range(10):
			val = 0
			it = []
			while val < price:
				pick = choice(items)
				it.append(pick)
				val += self.price(pick)
			if m_val<val:
				m_items = it
				v_val = val
		return { i:m_items.count(i) for i in set(m_items) }

	def max_buy(self, time):
		raise NotImplemented()

	def max_sell(self, time):
		raise NotImplemented()

	def income_coef(self, time):
		raise NotImplemented()

	def generate_one(self, time):

		buy = self.buying_entities(time)
		sell = self.selling_entities(time)

		if random()<0.5:
			var = choice(buy)
			buy.pop(buy.index(var))
		else:
			var = choice(sell)
			sell.pop(sell.index(var))

		auction = self.create_auction_object()
		auction.save()

		buy_c = self.get_items_to_price(self.max_buy(time), buy)
		sell_c = self.get_items_to_price(self.max_sell(time), sell)

		for ent, am in buy_c.items():
			self.add_auction_item(auction, ent, -am)
		for ent, am in sell_c.items():
			self.add_auction_item(auction, ent, am)

		var_min = self.estimate_price(auction, self.income_coef(time))
		auction.var_min = var_min
		auction.save()

	def estimate_price(self, auction, coef):
		diff = sum(self.model.get_entity(item.entity.name).price * item.amount for item in auction.auctioneditem_set.all())
		return diff * coef


	def add_auction_item(self,auction,entity_name,amount,visible=True,will_sell=True):
		item = AuctionedItem(
			auction=auction,
			entity=self.model.get_entity(entity_name),
			amount=amount,
			visible=visible,
			will_sell=will_sell
			)
		item.save()
		return item

	def generate(self):
		raise NotImplemented()

class TrivialSeller(SellerBase):
	
	def __init__(self, model):
		super().__init__(model)

	def max_buy(self, time):
		return 10

	def max_sell(self, time):
		return 10

	def income_coef(self, time):
		return 1

	def generate(self):
		self.generate_one(0.01)

	def buying_entities(self,time):
		return ["Kel","Písek"]

	def selling_entities(self,time):
		return ["Křemen", "Žula"]


class StaticAuction(SellerBase):
	def __init__(self, coef, *args, **kwargs):
		self.estimate = not 'var_min' in kwargs.keys()
		if self.estimate:
			kwargs['var_min'] = 0
		self.coef = coef
		self.b = BlackAuction(*args, **kwargs)
		self.b.save()

	def __enter__(self):
		return self.b

	def __exit__(self, exc_type, exc_val, exc_tb):
		if self.estimate:
			self.estimate_price(self.b, self.coef)
			self.b.save()

def generate_blackmarket(buf):
	
	x = buf.get_entity("Kel")
	print("tohle",vars(x))
	print(type(x))
	print(x.price)

	sellers = [
		#LicenceBAGenerator(buf),
		#RandomStuffRiscantBAGenerator(buf)
		TrivialSeller(buf),
		]

	BlackAuction.objects.all().delete()


	for f in sellers:
		f.generate()

	def e(*args, **kwargs):
		return (buf.get_or_create_ent(*args, **kwargs))

	with StaticAuction(1,
			begin=datetime.timedelta(minutes=10),
			var_entity=e('Oheň')) as b:
		b.add_item(e('Žula'), 1)
		b.add_item(e('Žula'), 1)

