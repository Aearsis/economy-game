from data.settings import *
from data.models import *
from data.blackmarket_pricelist import *

import datetime

from auctions.models import *
from core.models import *

from random import *

from math import isinf

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

class EvolvingSetting:
	
	def __init__(self, setting):
		'''setting: list of pairs (percent_time, value) or a dict. In percent_time
		a setting will be changed to value
		'''

		self.setting = dict(setting)
		assert 0 in self.setting, 'setting must contain 0 (initial value)'
		assert all(0<= x <=1 for x in self.setting.keys())

	def value_in_time(self,time):
		m = max(x for x in self.setting.keys() if x<=time)
		return self.setting[m]



class SellerBase:
	'''abstract class'''

	def __init__(self, buf):
		self.game_len = Game.the_row().length
		self.model = buf
		self.seller_name = "base"

	def create_auction_object(self,entity="Ticho"):
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
		return self.model.get_price(entity)

	def get_items_to_price(self, price, items):
		'''choices random items whose sum of price is as nearest as posible to
		price

		it chooses it 10-times randomly and returns the best attempt
		'''

		if not items:
			return {}

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


	# abstract methods
	def max_buy(self, time):
		raise NotImplemented()

	def max_sell(self, time):
		raise NotImplemented()

	def income_coef(self, time):
		raise NotImplemented()

	def buying_entities(self,time):
		raise NotImplemented()

	def selling_entities(self,time):
		raise NotImplemented()

	def generate_one(self, time):

		sell = self.selling_entities(time)
		buy = [ x for x in self.buying_entities(time) if not x in sell ]

		if random()<0.5 or not buy:
			var = choice(sell)
			sell.pop(sell.index(var))
		else:
			var = choice(buy)
			buy.pop(buy.index(var))
		
		auction = self.create_auction_object()
		auction.save()

		sell_c = self.get_items_to_price(self.max_sell(time), sell)
		buy_c = self.get_items_to_price(self.max_buy(time), buy)

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


class RandomStuffRiscantSeller(SellerBase):

	def __init__(self, model):
		super().__init__(model)
		self.name = "Dr. Kámen"

		# risk
		self.risks = EvolvingSetting({ 0: 0, 0.1: 0.1, 0.15: 0.15, 0.4: 0.2, 0.5: 0.01, 0.65: 0.25 })

		# average time between auctions in seconds
		self.spans = EvolvingSetting({ 0: 60, 0.1: 40, 0.2: 30, 0.25: 20 })



		# průměrný profit z výdělků
		self.profits = EvolvingSetting({0: 2})

		# věci, za které bude černý trh nakupovat
		self.buying_stuff = EvolvingSetting({
			0: minable_1,
			0.05: minable,
			0.1: minable+markatable,
			0.3: all_goods
		})

		self.buying_entities = self.buying_stuff.value_in_time

		# věci, které se v tu dobu budou prodávat
		self.selling_stuff = EvolvingSetting({
			0: list(set(minable+markatable)),
			0.1: list(set(minable + markatable + strategical)),
			# k nákupu jsou i aukce
			0.9: all_goods
		})

		self.selling_entities = self.selling_stuff.value_in_time

		self.max_buy_setting = EvolvingSetting({
			0: 100,
			0.1: 200,
			0.12:10000,
			0.22: 10**8
		})

		self.max_buy = self.max_buy_setting.value_in_time

		self.max_sell_setting = EvolvingSetting({
			0: 100,
			0.1: 200,
			0.12:10000,
			0.22: 10**8
		})

		self.max_sell = self.max_sell_setting.value_in_time


		self.income_coef_setting = EvolvingSetting({
			0: 1
		})

		self.income_coef = self.income_coef_setting.value_in_time




		# maximální počet druhů položek v aukci (když jich je moc, tak je to
		# nepřehledný)
		self.maxitems = EvolvingSetting({
			0:1,
			0.3:5,
			# neomezený počet: tohle bude brutální!
			0.6:len(all_goods)
		})


	def generate(self):
		#for x in range(0,100,20):
		#	self.generate_one(x/100)

		#return
# TODO

		seconds = 0
		perc_time = 0
		while perc_time < 1:
			span = self.spans.value_in_time(perc_time)
			seconds += span
			perc_time = seconds/self.game_len.seconds

			self.generate_one(perc_time)







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
		return ["Ticho","Písek"]

	def selling_entities(self,time):
		return ["Křemen", "Žula"]


# static
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

	sellers = [
#		TrivialSeller(buf),
		RandomStuffRiscantSeller(buf),
		]

	BlackAuction.objects.all().delete()


	for f in sellers:
		f.generate()

#	def e(*args, **kwargs):
#		return (buf.get_or_create_ent(*args, **kwargs))

#	with StaticAuction(1,
#			begin=datetime.timedelta(minutes=10),
#			var_entity=e('Oheň')) as b:
#		b.add_item(e('Žula'), 1)
#		b.add_item(e('Žula'), 1)

